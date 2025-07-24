import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import uuid

matplotlib.use("Agg")  # For non-GUI environments


def analyzeSymptoms(userSymptoms):
    print("Symptoms Received:", userSymptoms)

    df = pd.read_csv("data/disease_dataset_info.csv")
    userSymptoms = set([s.strip().lower() for s in userSymptoms])

    scores = {}
    for _, row in df.iterrows():
        disease = row["disease"]
        diseaseSymptoms = set(sym.strip().lower() for sym in row["symptoms"].split(","))
        matchCount = len(userSymptoms & diseaseSymptoms)
        total = len(diseaseSymptoms)
        score = matchCount / total if total else 0
        scores[disease] = round(score, 2)

    # Sort and take top 6 non-zero scoring diseases
    topScores = {
        disease: score
        for disease, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if score > 0
    }
    topScores = dict(list(topScores.items())[:6])

    if not topScores:
        return {}, None

    # ✅ Use /tmp for Render-safe storage
    os.makedirs("/tmp", exist_ok=True)

    # Plotting
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

    plt.tight_layout(pad=2)

    filename = f"{uuid.uuid4().hex}.png"
    path = os.path.join("/tmp", filename)
    plt.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close()

    return topScores, filename