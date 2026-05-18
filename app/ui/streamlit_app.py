# UI LAYER
# This file acts as controller between user and backend modules
import sys
import os


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)

import streamlit as st
import json
import time
from streamlit_autorefresh import st_autorefresh
from app.engines.voice_engine import speak, listen
from app.services.attention_client import get_attention
from app.engines.question_engine import answer_question


from app.services.config import TOPIC_PATH, ATTENTION_PATH, CONTROL_PATH

if "studying" not in st.session_state:
    st.session_state.studying = False

if "listening" not in st.session_state:
    st.session_state.listening = False

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Learning Assistant", layout="wide")
if not st.session_state.listening:
    st_autorefresh(interval=1000, key="attention_refresh")
st.title("🧠 AI Voice Learning Assistant")


st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}

/* Top Control Bar */
.control-bar {
    background: #020617;
    padding: 1rem;
    border-radius: 14px;
    margin-bottom: 1rem;
    box-shadow: 0 8px 25px rgba(0,0,0,0.35);
}

/* Cards */
.card {
    background: #020617;
    padding: 1rem;
    border-radius: 14px;
    margin-bottom: 1rem;
}

/* Buttons */
.stButton>button {
    height: 3rem;
    border-radius: 10px;
    font-size: 1rem;
}

/* Attention badge */
.att-badge {
    font-size: 1.4rem;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="control-bar">', unsafe_allow_html=True)

c1, c2, c3 = st.columns([2,2,4])

with c1:
    if st.button("▶ Start Studying"):
        st.session_state.studying = True
        with open(CONTROL_PATH, "w") as f:
            json.dump({"studying": True}, f)
with c2:
    if st.button("⏹ Stop Studying"):
        st.session_state.studying = False
        with open(CONTROL_PATH, "w") as f:
            json.dump({"studying": False}, f)

with c3:
    if st.session_state.studying:
        st.success("🟢 Study Session Active")
    else:
        st.warning("🟡 Study Session Inactive")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- LOAD JSON ----------------
with open(TOPIC_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

topics_data = data["topics"]
topics = list(topics_data.keys())

# ---------------- TOPIC SELECTION ----------------
selected_topic = st.radio("📚 Select Topic", topics, horizontal=True)
topic = topics_data[selected_topic]

# ---------------- SHOW FULL JSON CONTENT ----------------
with st.expander("📘 Topic Content", expanded=True):
    st.markdown(f"### {topic.get('topic', selected_topic)}")
    st.info(topic.get("definition", ""))

    st.markdown("#### 🔹 Key Concepts")
    for c in topic.get("key_concepts", []):
        st.markdown(f"**{c['name']}** — {c['description']}")

    st.markdown("#### 🔹 Types")
    for t in topic.get("types", []):
        st.markdown(f"**{t['type']}** — {t['description']}")



# ---------------- ATTENTION STATUS ----------------
st.markdown("---")
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("👀 Attention Status")

att, ts = get_attention()

if time.time() - ts > 3:
    st.warning("⚠ Attention engine not responding")
else:
    color_map = {
        "Attentive": "🟢",
        "Confused": "🟡",
        "Distracted": "🟠",
        "Sleepy": "🔴"
    }
    st.markdown(
        f"<div class='att-badge'>{color_map.get(att,'⚪')} {att}</div>",
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)


# ---------------- QUESTION ----------------
st.markdown("---")
with st.expander("🎤 Ask a Question", expanded=True):

    if st.session_state.studying:

        colA, colB = st.columns(2)

        with colA:
            if st.button("🎙 Ask by Voice"):
                st.session_state.listening = True
                q = listen()
                st.session_state.listening = False

                if q:
                    st.write("🗣 You asked:", q)
                    ans = answer_question(q.lower(), topic)
                    st.success(ans)
                    speak(ans)

        with colB:
            typed = st.text_input("⌨ Type your question")
            if typed:
                ans = answer_question(typed.lower(), topic)
                st.success(ans)
                speak(ans)
    else:
        st.info("Start studying to enable questions.")

