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

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Analyze symptoms and return results + plot
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    symptoms = data.get("symptoms", [])
    
    if not symptoms:
        return jsonify({"error": "No Symptoms Provided"}), 400

    results, plotPath = analyzeSymptoms(symptoms)
    return jsonify({"results": results, "plotUrl": f"/plot/{plotPath}"})


# Serve plot image
@app.route("/plot/<filename>")
def getPlot(filename):
    return send_file(f"static/plots/{filename}", mimetype="image/png")


# Generate AI-driven health advice using OpenRouter DeepSeek model
@app.route("/generate_advice", methods=["POST"])
def generateAdvice():
    data = request.get_json()
    diseases = data.get("diseases", [])

    if not diseases:
        return jsonify({"error": "No diseases provided"}), 400

    # Prompt format
    prompt = (
        "Give clear and concise precautions and solutions for each of the following diseases. "
        "Return it in the following JSON format:\n\n"
        "{\n"
        "  'Disease Name': {\n"
        "    'precautions': 'Precaution details here...',\n"
        "    'solution': 'Solution details here...'\n"
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
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "DiseaseSymptomMapper"
            },
            data=json.dumps({
                "model": "deepseek/deepseek-r1-0528:free",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )

        result = response.json()
        advice_text = result["choices"][0]["message"]["content"]

        # Try to parse the advice as a dict
        try:
            advice_json = ast.literal_eval(advice_text)
            return jsonify({"advice": advice_json})
        except Exception as parse_error:
            print("Parsing failed, returning raw text")
            return jsonify({"advice": {"raw": advice_text}})

    except Exception as e:
        print("OpenRouter API error:", e)
        return jsonify({"error": "Failed to generate advice"}), 500


# Run app
if __name__ == "__main__":
    app.run(debug=True)
