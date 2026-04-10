import streamlit as st
from chat_service import process_chat, load_history

# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="Mental Health Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 Mental Health Chatbot")
st.write("Talk freely. This is your safe space 💙")

# -----------------------
# Session state (current chat only)
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_history" not in st.session_state:
    st.session_state.show_history = False

# -----------------------
# Toggle history button
# -----------------------
if st.button("📜 Show / Hide Server History"):
    st.session_state.show_history = not st.session_state.show_history

# -----------------------
# Show server history (optional)
# -----------------------
if st.session_state.show_history:
    st.subheader("📜 Saved History (Server)")

    history = load_history()

    for msg in history:
        if msg["role"] == "user":
            st.markdown(f"**🧑 You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**🤖 Bot:** {msg['content']}")

    st.divider()

# -----------------------
# Show current session chat
# -----------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])

# -----------------------
# Input box
# -----------------------
user_input = st.chat_input("Type your message...")

if user_input:

    # show user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # get response from backend
    result = process_chat(user_input)

    if "error" in result:
        bot_reply = f"⚠️ Error: {result['error']}"
    else:
        bot_reply = result["reply"]

    # show bot message
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    with st.chat_message("assistant"):
        st.write(bot_reply)

    # optional info (emotion + practice)
    if "emotion" in result:
        st.caption(f"Detected emotion: {result['emotion']}")

    if result.get("practice"):
        st.info("Suggested Practices:")
        for p in result["practice"]:
            st.write(f"- {p}")