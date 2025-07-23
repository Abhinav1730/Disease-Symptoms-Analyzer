from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from analyzer import analyzeSymptoms
from dotenv import load_dotenv
import os
import json
import ast

load_dotenv()

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Ensure the plots folder exists
os.makedirs(os.path.join(app.static_folder, "plots"), exist_ok=True)


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    symptoms = data.get("symptoms", [])

    if not symptoms:
        return jsonify({"error": "No Symptoms Provided"}), 400

    results, plotPath = analyzeSymptoms(symptoms)

    base_url = os.getenv("BASE_URL") or request.host_url.rstrip("/")
    plot_url = f"{base_url}/plot/{plotPath}" if plotPath else None

    return jsonify({"results": results, "plotUrl": plot_url})


@app.route("/plot/<filename>")
def get_plot(filename):
    plot_dir = os.path.join(app.static_folder, "plots")
    file_path = os.path.join(plot_dir, filename)

    if not os.path.isfile(file_path):
        return jsonify({"error": "Plot not found"}), 404

    return send_from_directory(plot_dir, filename, mimetype="image/png")


@app.route("/generate_advice", methods=["POST"])
def generate_advice():
    data = request.get_json()
    diseases = data.get("diseases", [])

    if not diseases:
        return jsonify({"error": "No diseases provided"}), 400

    prompt = (
        "Provide short but clear precautions and treatment solutions for each of the following diseases "
        "in the following JSON format (use double quotes for valid JSON):\n\n"
        "{\n"
        '  "Disease Name": {\n'
        '    "precautions": "Precaution details here...",\n'
        '    "solution": "Solution details here..."\n'
        "  },\n"
        "  ...\n"
        "}\n\n"
        f"Diseases: {', '.join(diseases)}"
    )

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://your-frontend-url.vercel.app",  # Update to actual deployed Vercel domain
                "X-Title": "DiseaseSymptomMapper",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-r1-0528:free",
                "messages": [{"role": "user", "content": prompt}]
            }),
        )

        result = response.json()
        advice_text = result["choices"][0]["message"]["content"]

        try:
            advice_json = json.loads(advice_text)
        except Exception:
            try:
                advice_json = ast.literal_eval(advice_text)
            except Exception:
                print("Advice parsing failed, returning raw text")
                return jsonify({"advice": {"raw": advice_text}})

        return jsonify({"advice": advice_json})

    except Exception as e:
        print("OpenRouter API error:", e)
        return jsonify({"error": "Failed to generate advice"}), 500


if __name__ == "__main__":
    app.run(debug=True)