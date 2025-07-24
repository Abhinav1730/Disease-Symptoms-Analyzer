from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import ast
import requests
from dotenv import load_dotenv
from analyzer import analyzeSymptoms  # Should return: results_dict, base64_plot_string

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://disease-symptoms-analyzer.vercel.app"}})

# ------------------ Analyze Symptoms ------------------ #
@app.route("/analyze", methods=["POST"])
def analyze():
    if not request.is_json:
        return jsonify({"error": "Invalid content type, expected JSON"}), 400

    data = request.get_json()
    symptoms = data.get("symptoms", [])

    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400

    try:
        results, plot_base64 = analyzeSymptoms(symptoms)

        return jsonify({
            "results": results,
            "plotBase64": f"data:image/png;base64,{plot_base64}" if plot_base64 else None
        })

    except Exception as e:
        print("Error in /analyze:", str(e))
        return jsonify({"error": "Something went wrong during analysis"}), 500

# ------------------ Generate Advice ------------------ #
@app.route("/generate_advice", methods=["POST"])
def generate_advice():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid content type, expected JSON"}), 400

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

        if response.status_code != 200:
            print("OpenRouter returned non-200 status:", response.status_code)
            print("Response body:", response.text)
            return jsonify({"error": "OpenRouter API failed"}), 500

        result = response.json()
        advice_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        if not advice_text:
            return jsonify({"error": "No advice received from model"}), 500

        try:
            advice_json = json.loads(advice_text)
        except Exception:
            try:
                advice_json = ast.literal_eval(advice_text)
            except Exception:
                print("Advice parsing failed. Raw response:\n", advice_text)
                return jsonify({"advice": {"raw": advice_text}})

        return jsonify({"advice": advice_json})

    except Exception as e:
        print("Error in /generate_advice:", str(e))
        return jsonify({"error": "Something went wrong in generating advice"}), 500

# ------------------ Run Server (for development only) ------------------ #
if __name__ == "__main__":
    app.run(debug=True)