import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import uuid

matplotlib.use("Agg")  # Non-interactive backend for server environments

def analyzeSymptoms(userSymptoms):
    print("Symptoms Received:", userSymptoms)

    # Read dataset
    df = pd.read_csv("data/disease_dataset_info.csv")

    # Clean user symptoms
    userSymptoms = set([s.strip().lower() for s in userSymptoms])

    # Score matching
    scores = {}
    for _, row in df.iterrows():
        disease = row["disease"]
        diseaseSymptoms = set(sym.strip().lower() for sym in row["symptoms"].split(","))
        matchCount = len(userSymptoms & diseaseSymptoms)
        total = len(diseaseSymptoms)
        score = matchCount / total if total else 0
        scores[disease] = round(score, 2)

    # Filter top non-zero scoring diseases
    topScores = {
        disease: score for disease, score in sorted(
            scores.items(), key=lambda x: x[1], reverse=True
        ) if score > 0
    }

    topScores = dict(list(topScores.items())[:6])  # Take top 6 non-zero matches

    if not topScores:
        return {}, None  # Nothing to plot if no matches

    # Ensure directory exists
    os.makedirs("static/plots", exist_ok=True)

    # Plotting
    plt.figure(figsize=(10, 5))
    diseases = list(topScores.keys())
    values = list(topScores.values())

    bars = plt.barh(diseases, values, color="orange", edgecolor="black")
    plt.xlabel("Match Score", fontsize=12, color='black')
    plt.ylabel("Diseases", fontsize=12, color='black')
    plt.title("Top Disease Matches Based on Symptoms", fontsize=14, color='black')
    plt.xlim(0, 1.0)
    plt.xticks(color='black')
    plt.yticks(color='black')
    plt.gca().invert_yaxis()  # Show highest match on top
    plt.tight_layout(pad=2)

    # Add values to bars
    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.2f}",
            va='center',
            fontsize=10,
            color='black'
        )

    # Save plot with unique filename
    filename = f"{uuid.uuid4().hex}.png"
    path = os.path.join("static/plots", filename)
    plt.savefig(path, bbox_inches="tight", facecolor='white')
    plt.close()

    return topScores, filename