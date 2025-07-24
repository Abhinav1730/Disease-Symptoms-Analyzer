import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64

matplotlib.use("Agg")

def analyzeSymptoms(userSymptoms):
    print("Symptoms Received:", userSymptoms)
    df = pd.read_csv("data/disease_dataset_info.csv")
    userSymptoms = set(s.strip().lower() for s in userSymptoms)

    scores = {}
    for _, row in df.iterrows():
        disease = row["disease"]
        diseaseSymptoms = set(sym.strip().lower() for sym in row["symptoms"].split(","))
        matchCount = len(userSymptoms & diseaseSymptoms)
        total = len(diseaseSymptoms)
        score = matchCount / total if total else 0
        scores[disease] = round(score, 2)

    topScores = {
        disease: score
        for disease, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if score > 0
    }
    topScores = dict(list(topScores.items())[:6])

    if not topScores:
        return {}, None

    diseases = list(topScores.keys())
    values = list(topScores.values())

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(diseases, values, color="orange", edgecolor="black")
    ax.set_xlabel("Match Score", fontsize=12, color="black")
    ax.set_title("Top Disease Matches Based on Symptoms", fontsize=14, color="black")
    ax.set_xlim(0, 1.0)
    ax.tick_params(axis="x", colors="black")
    ax.tick_params(axis="y", colors="black")
    ax.invert_yaxis()

    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.2f}",
            va="center",
            fontsize=10,
            color="black",
        )

    # Convert plot to base64
    buffer = BytesIO()
    plt.tight_layout(pad=2)
    plt.savefig(buffer, format="png", bbox_inches="tight", facecolor="white")
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    return topScores, image_base64