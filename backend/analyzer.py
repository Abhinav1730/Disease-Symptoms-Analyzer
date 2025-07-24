import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import uuid

matplotlib.use("Agg")  # Ensures plot works in non-GUI environments

def analyzeSymptoms(userSymptoms):
    print("Symptoms Received:", userSymptoms)

    # Loading disease dataset
    df = pd.read_csv("data/disease_dataset_info.csv")

    # Normalizing user input symptoms
    userSymptoms = set(s.strip().lower() for s in userSymptoms)

    # Match scoring logic
    scores = {}
    for _, row in df.iterrows():
        disease = row["disease"]
        diseaseSymptoms = set(sym.strip().lower() for sym in row["symptoms"].split(","))
        matchCount = len(userSymptoms & diseaseSymptoms)
        total = len(diseaseSymptoms)
        score = matchCount / total if total else 0
        scores[disease] = round(score, 2)

    # Filtering top 6 diseases with non-zero match
    topScores = {
        disease: score
        for disease, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if score > 0
    }
    topScores = dict(list(topScores.items())[:6])

    # Return early if no relevant matches
    if not topScores:
        return {}, None

    # Saving plot to static/plots/
    plot_dir = os.path.join("static", "plots")
    os.makedirs(plot_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.png"
    path = os.path.join(plot_dir, filename)

    # Plotting top matched disease
    diseases = list(topScores.keys())
    values = list(topScores.values())

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(diseases, values, color="orange", edgecolor="black")
    ax.set_xlabel("Match Score", fontsize=12, color="black")
    ax.set_title("Top Disease Matches Based on Symptoms", fontsize=14, color="black")
    ax.set_xlim(0, 1.0)
    ax.tick_params(axis="x", colors="black")
    ax.tick_params(axis="y", colors="black")
    ax.invert_yaxis()  # Show highest matched disease on top

    # Add score labels to bars
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

    # Save the plot image
    plt.tight_layout(pad=2)
    plt.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close()

    return topScores, filename