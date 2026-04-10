import pandas as pd
import random

# Load once (not every call)
#
#PRACTICE_PATH = "D:\Graduation_Project\mental_health_bot\project\Practice.xls"
PRACTICE_PATH = "Practice.xls"
#practice_df = pd.read_excel(PRACTICE_PATH)
practice_df = pd.read_excel("Practice.xlsx", engine="openpyxl")

def select_practice(emotion, k=5):
    """
    Select k random practices for given emotion.
    Safe, cached, and fault tolerant.
    """

    # Normalize emotion
    emotion = emotion.lower().strip()

    # If column missing → fallback
    if emotion not in practice_df.columns:
        emotion = "neutral"

    # Drop empty cells
    practices = practice_df[emotion].dropna().tolist()

    if len(practices) == 0:
        return "Try slow breathing and grounding exercises."

    # Sample safely
    k = min(k, len(practices))
    selected = random.sample(practices, k)

    advice = "\n"
    for p in selected:
        advice += f"- {p}\n"

    return selected
