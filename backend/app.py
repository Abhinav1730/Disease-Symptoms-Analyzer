from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from analyzer import analyzeSymptoms
from dotenv import load_dotenv
import os
import json
import ast

# Load environment variables
load_dotenv()

# Create Flask app with static folder
app = Flask(__name__, static_folder="static")
CORS(app)

# ------------------ /analyze Endpoint ------------------ #
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    symptoms = data.get("symptoms", [])

    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400

    results, plot_filename = analyzeSymptoms(symptoms)

    # Get base URL from env or current request
    base_url = os.getenv("BASE_URL") or request.host_url.rstrip("/")
    plot_url = f"{base_url}/plot/{plot_filename}" if plot_filename else None

    return jsonify({"results": results, "plotUrl": plot_url})


# ------------------ /plot/<filename> Image Endpoint ------------------ #
@app.route("/plot/<filename>")
def get_plot(filename):
    plot_path = os.path.join(app.static_folder, "plots", filename)

    if not os.path.isfile(plot_path):
        return jsonify({"error": "Plot not found"}), 404

    return send_file(plot_path, mimetype="image/png")


# ------------------ /generate_advice Endpoint ------------------ #
@app.route("/generate_advice", methods=["POST"])
def generate_advice():
    data = request.get_json()
    diseases = data.get("diseases", [])

    if not diseases:
        return jsonify({"error": "No diseases provided"}), 400

    # Prompt to get advice in valid JSON format
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
                "HTTP-Referer": "https://disease-symptoms-analyzer.vercel.app",  # ✅ Your frontend
                "X-Title": "DiseaseSymptomMapper",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-r1-0528:free",
                "messages": [{"role": "user", "content": prompt}]
            }),
        )

        result = response.json()
        advice_text = result["choices"][0]["message"]["content"]

        # Trying to parsing advice safely
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


# ------------------ Run Dev Server ------------------ #
if __name__ == "__main__":
    app.run(debug=True)