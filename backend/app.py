from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from analyzer import analyzeSymptoms

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    symptoms = data.get("symptoms", [])
    if not symptoms:
        return jsonify({"error": "No Symptoms Provided"}), 400

    results, plotPath = analyzeSymptoms(symptoms)
    return jsonify({"results": results, "plotUrl": f"/plot/{plotPath}"})


@app.route("/plot/<filename>")
def getPlot(filename):
    return send_file(f"static/plots/{filename}", mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True)
