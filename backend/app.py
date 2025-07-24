from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import ast
import requests
from dotenv import load_dotenv
from analyzer import analyzeSymptoms  # Now returns base64-encoded image

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)

# ------------------ /analyze Endpoint ------------------ #
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    symptoms = data.get("symptoms", [])

    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400

    # Call analyzer
    results, plot_base64 = analyzeSymptoms(symptoms)

    return jsonify({
        "results": results,
        "plotBase64": f"data:image/png;base64,{plot_base64}" if plot_base64 else None
    })

# ------------------ /generate_advice Endpoint ------------------ #
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
                "HTTP-Referer": "https://disease-symptoms-analyzer.vercel.app",
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

# ------------------ Run Dev Server ------------------ #
if __name__ == "__main__":
    app.run(debug=True)