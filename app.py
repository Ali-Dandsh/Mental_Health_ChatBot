import streamlit as st
from openai import OpenAI
from chat_service import process_chat, load_history

# -----------------------
# Secrets (Streamlit)
# -----------------------
API_KEY = st.secrets["API_KEY"]
BASE_URL = st.secrets["BASE_URL"]
MODEL_NAME = st.secrets["MODEL_NAME"]

# -----------------------
# OpenAI Client
# -----------------------
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# -----------------------
# Page config
# -----------------------
st.set_page_config(
    page_title="Mental Health Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Mental Health Chatbot")
st.write("Talk freely. This is your safe space 💙")

# -----------------------
# Session state
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_history" not in st.session_state:
    st.session_state.show_history = False

# -----------------------
# Toggle history
# -----------------------
if st.button("📜 Show / Hide Server History"):
    st.session_state.show_history = not st.session_state.show_history

if st.session_state.show_history:
    st.subheader("📜 Saved History (Server)")

    history = load_history()

    for msg in history:
        if msg["role"] == "user":
            st.markdown(f"**🧑 You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 Bot:** {msg['content']}")

    st.divider()

# -----------------------
# Show current chat
# -----------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -----------------------
# Input
# -----------------------
user_input = st.chat_input("Type your message...")

if user_input:

    # user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # backend call
    try:
        result = process_chat(user_input, client, MODEL_NAME)
    except Exception as e:
        st.error(f"App Error: {e}")
        st.stop()

    # handle error safely
    if "error" in result:
        bot_reply = f"⚠️ Error: {result['error']}"
    else:
        bot_reply = result.get("reply", "Sorry, I couldn't generate a response.")

    # save bot message
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # show bot message
    with st.chat_message("assistant"):
        st.write(bot_reply)

    # (اختياري) معلومات إضافية بشكل أنضف
    with st.expander("More details"):
        if "emotion" in result:
            st.caption(f"Detected emotion: {result['emotion']}")

        if result.get("practice"):
            st.write("Suggested Practices:")
            for p in result["practice"]:
                st.write(f"- {p}")
