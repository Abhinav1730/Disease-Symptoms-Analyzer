from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import ast
import requests
from dotenv import load_dotenv
from analyzer import analyzeSymptoms  # This must return: results_dict, base64_plot_string

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://disease-symptoms-analyzer.vercel.app"}})  # Enable CORS for all origins (good for Vercel frontend)

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
        # Call your analyzer function
        results, plot_base64 = analyzeSymptoms(symptoms)

        # Response with results and base64 image string
        return jsonify({
            "results": results,
            "plotBase64": f"data:image/png;base64,{plot_base64}" if plot_base64 else None
        })

    except Exception as e:
        print("Error in analyzer:", str(e))
        return jsonify({"error": "Something went wrong during analysis"}), 500

# ------------------ Generate Advice ------------------ #
@app.route("/generate_advice", methods=["POST"])
def generate_advice():
    data = request.get_json()
    diseases = data.get("diseases", [])

    if not diseases:
        return jsonify({"error": "No diseases provided"}), 400

    # Prompt for AI API
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

        # Try parsing the returned advice
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
        print("OpenRouter API error:", str(e))
        return jsonify({"error": "Failed to generate advice"}), 500

# ------------------ Run Server (for dev only) ------------------ #
if __name__ == "__main__":
    app.run(debug=True)