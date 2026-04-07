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
    # limit size
    messages = messages[-50:]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


# -----------------------------
# Language Detection
# -----------------------------
def detect_language(text):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Return ONLY 'ar' or 'en'."},
            {"role": "user", "content": text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip().lower()


# -----------------------------
# Dynamic System Prompt
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
# Translate (only if Arabic)
# -----------------------------
def translate(text, lang):
    if lang == "en":
        return text

    response = client.chat.completions.create(
        model=MODEL_NAME,
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
def classify_emotion(text):
    response = client.chat.completions.create(
        model=MODEL_NAME,
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
# Generate Chat Response
# -----------------------------
def generate_response(messages, user_input):
    messages.append({"role": "user", "content": user_input})

    trimmed_messages = messages[-20:]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=trimmed_messages,
        temperature=0.7
    )

    reply = response.choices[0].message.content.strip()

    messages.append({"role": "assistant", "content": reply})

    # Save history
    save_history(messages)

    return reply


# -----------------------------
# Main Chat Loop
# -----------------------------
def chat():
    print("Mental Health Support Chatbot")
    print("Type 'exit' to quit.\n")

    messages = load_history()
    first_turn = True
    lang = "en"

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            print("Bot: Take care. I'm always here to listen.")
            break

        try:
            if first_turn:
                lang = detect_language(user_input)

                # لو مفيش history
                if not messages:
                    messages.append({
                        "role": "system",
                        "content": get_system_prompt(lang)
                    })

                emotion = classify_emotion(user_input)
                practice = select_practice(emotion)

                first_turn = False
            else:
                practice = ""

            reply = generate_response(messages, user_input)

            print("Bot:", reply)
            print("-" * 50)

            if practice:
                print("تمارين مقترحة:" if lang == "ar" else "Suggested Practice:")

                for p in practice:
                    print(f"- {translate(p, lang)}")

        except Exception as e:
            print("Error:", e)


# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    chat()