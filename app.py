import streamlit as st
import requests
import json

# --- 100% BRANDING ---
st.set_page_config(page_title="RV AI - Personal Assistant", page_icon="https://i.postimg.cc/5y14PWfB/RV-AI.jpg")

# CSS පාවිච්චි කරලා පෙනුම වෙනස් කරමු (Custom Style)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextInput { border-radius: 20px; }
    .logo-text { font-size: 30px; font-weight: bold; color: #00aaff; }
    </style>
    """, unsafe_allow_html=True)

# Logo සහ Title
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://i.postimg.cc/5y14PWfB/RV-AI.jpg", width=60)
with col2:
    st.markdown('<p class="logo-text">RV AI LANKA</p>', unsafe_allow_html=True)

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# පරණ මැසේජ් පෙන්වීම
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("RV AI එකෙන් ඕනෑම දෙයක් අහන්න..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ollama එකට කතා කිරීම
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # මෙතන 'ollama' කියන්නේ ඔබේ coolify service එකේ නම
        url = "http://ollama:11434/api/generate"
        payload = {"model": "llama3", "prompt": prompt, "stream": True}
        
        res = requests.post(url, json=payload, stream=True)
        for line in res.iter_lines():
            if line:
                chunk = json.loads(line)
                full_response += chunk.get("response", "")
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- SETTINGS & HISTORY (SIDEBAR) ---
with st.sidebar:
    st.title("RV AI Settings")
    st.info("Powered by RV Developers")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
