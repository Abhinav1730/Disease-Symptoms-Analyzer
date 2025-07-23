from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from analyzer import analyzeSymptoms
from dotenv import load_dotenv
import os
import json
import ast

load_dotenv()

app = Flask(__name__)
CORS(app)


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
def getPlot(filename):
    full_path = os.path.join(app.root_path, "static", "plots", filename)
    return send_file(full_path, mimetype="image/png")


@app.route("/generate_advice", methods=["POST"])
def generateAdvice():
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
                "HTTP-Referer": "http://localhost:5173",  # Optional for OpenRouter
                "X-Title": "DiseaseSymptomMapper",
            },
            data=json.dumps(
                {
                    "model": "deepseek/deepseek-r1-0528:free",
                    "messages": [{"role": "user", "content": prompt}],
                }
            ),
        )

        result = response.json()
        advice_text = result["choices"][0]["message"]["content"]

        # Try parsing as JSON string
        try:
            advice_json = json.loads(advice_text)
        except Exception:
            try:
                advice_json = ast.literal_eval(advice_text)
            except Exception:
                print("Parsing failed, returning raw text")
                return jsonify({"advice": {"raw": advice_text}})

        return jsonify({"advice": advice_json})

    except Exception as e:
        print("OpenRouter API error:", e)
        return jsonify({"error": "Failed to generate advice"}), 500


if __name__ == "__main__":
    app.run(debug=True)
