import streamlit as st
import requests
import json

# --- 100% BRANDING & UI SETTINGS ---
st.set_page_config(page_title="RV AI", page_icon="https://i.postimg.cc/5y14PWfB/RV-AI.jpg", layout="wide")

# Gemini/ChatGPT Style CSS
st.markdown("""
    <style>
    .main { background-color: #131314; color: #e3e3e3; }
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    .stChatFloatingInputContainer { background-color: #1e1f20; }
    /* වටකුරු ලෝගෝ එක */
    .logo-img { border-radius: 50%; border: 2px solid #00aaff; }
    .stButton>button { border-radius: 20px; background-color: #00aaff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Header Section
col1, col2 = st.columns([1, 8])
with col1:
    st.image("https://i.postimg.cc/5y14PWfB/RV-AI.jpg", width=70) # ලෝගෝ එක
with col2:
    st.title("RV AI LANKA")
    st.caption("Advanced AI Assistant by RV Developers")

st.divider()

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# මැසේජ් පෙන්වීම
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("RV AI එකෙන් ඕනෑම දෙයක් අහන්න..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # මෙතන 'rv-ai-core' යනු ඔබ දුන් container name එකයි
            url = "http://172.17.0.1:11434/api/generate"
            payload = {"model": "llama3", "prompt": prompt, "stream": True}
            
            res = requests.post(url, json=payload, stream=True, timeout=10)
            for line in res.iter_lines():
                if line:
                    chunk = json.loads(line)
                    full_response += chunk.get("response", "")
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Ollama සම්බන්ධ කරගැනීමට නොහැකි විය. කරුණාකර 'rv-ai-core' සේවාව ක්‍රියාත්මකදැයි බලන්න.")
            full_response = "Error: Connection failed."

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar
with st.sidebar:
    st.image("https://i.postimg.cc/5y14PWfB/RV-AI.jpg", width=150)
    st.header("RV AI Control")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
