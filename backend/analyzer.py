import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import uuid


def analyzeSymptoms(userSymptoms):
    df = pd.read_csv("data/disease_dataset_info.csv")
    userSymptoms = set([s.strip().lower() for s in userSymptoms])

    scores = {}
    for _, row in df.iterrows():
        disease = row["disease"]
        diseaseSymptoms = set(
            [sym.strip().lower() for sym in row["symptoms"].split(",")]
        )
        matchCount = len(userSymptoms & diseaseSymptoms)
        total = len(diseaseSymptoms)
        score = matchCount / total if total else 0
        scores[disease] = round(score, 2)

    topScores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5])

    # creating plot
    plt.figure(figsize=(8, 5))
    plt.barh(list(topScores.keys()), list(scores.values()), color="skyblue")
    plt.xlabel("Match Score")
    plt.ylabel("Top Disease Matches")
    filename = f"{uuid.uuid4().hex}.png"
    path = os.path.join("static/plots", filename)
    plt.savefig(path)
    plt.close()

    return scores, filename
