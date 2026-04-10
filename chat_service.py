import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from practice_selector import select_practice

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5-mini")

if not API_KEY:
    raise ValueError("API_KEY not found in .env file")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL if BASE_URL else None
)

# -----------------------------
# File for saving history
# -----------------------------
HISTORY_FILE = "chat_history.json"


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(messages):
    messages = messages[-50:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


# -----------------------------
# Language Detection
# -----------------------------
def detect_language(text, client, model_name):
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "Return ONLY 'ar' or 'en'."},
            {"role": "user", "content": text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip().lower()


# -----------------------------
# System Prompt
# -----------------------------
def get_system_prompt(lang):
    if lang == "ar":
        return """
أنت شات بوت داعم للصحة النفسية.
أنت لست طبيباً.
أنت لا تقوم بالتشخيص.
تفاعل بتعاطف ودعم.
إذا بدا أنك على وشك التعرض لأزمة، انصح بالاتصال بخدمات الطوارئ.
"""
    else:
        return """
You are a supportive mental health chatbot.
You are NOT a medical doctor.
You do NOT diagnose.
Respond empathetically and supportively.
If crisis intent appears, advise contacting emergency support.
"""


# -----------------------------
# Translate
# -----------------------------
def translate(text, lang, client, model_name):
    if lang == "en":
        return text

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "Translate to simple Egyptian Arabic."},
            {"role": "user", "content": text}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# -----------------------------
# Emotion Classification
# -----------------------------
def classify_emotion(text, client, model_name):
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "Return ONLY one word from: anger, disgust, fear, joy, neutral, sadness, surprise."
            },
            {"role": "user", "content": text}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()


# -----------------------------
# Generate Response
# -----------------------------
def generate_response(messages, user_input, client, model_name):
    messages.append({"role": "user", "content": user_input})

    trimmed_messages = messages[-20:]

    response = client.chat.completions.create(
        model=model_name,
        messages=trimmed_messages,
        temperature=0.7
    )

    reply = response.choices[0].message.content.strip()

    messages.append({"role": "assistant", "content": reply})

    save_history(messages)

    return reply


# -----------------------------
# MAIN API FUNCTION
# -----------------------------
def process_chat(user_input, client, model_name):
    messages = load_history()
    first_turn = len(messages) == 0

    try:
        if first_turn:
            lang = detect_language(user_input, client, model_name)

            messages.append({
                "role": "system",
                "content": get_system_prompt(lang)
            })

            emotion = classify_emotion(user_input, client, model_name)
            practice = select_practice(emotion)

        else:
            lang = "ar" if "أنت" in messages[0]["content"] else "en"
            emotion = classify_emotion(user_input, client, model_name)
            practice = []

        reply = generate_response(messages, user_input, client, model_name)

        if practice and lang == "ar":
            practice = [
                translate(p, lang, client, model_name)
                for p in practice
            ]

        return {
            "reply": reply,
            "emotion": emotion,
            "practice": practice
        }

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# CLI TEST (optional)
# -----------------------------
def chat():
    print("Mental Health Support Chatbot")
    print("Type 'exit' to quit.\n")

    messages = load_history()

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("Bot: Take care.")
            break

        result = process_chat(user_input, client, MODEL_NAME)

        if "error" in result:
            print("Bot ERROR:", result["error"])
        else:
            print("Bot:", result["reply"])

            if result["practice"]:
                print("Suggested Practice:")
                for p in result["practice"]:
                    print("-", p)

        print("-" * 50)


if __name__ == "__main__":
    chat()
