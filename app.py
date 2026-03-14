import streamlit as st
import requests
import json
import sqlite3
import hashlib
from datetime import datetime

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('rv_ai_users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS chat_history(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, title TEXT, messages TEXT, timestamp DATETIME)')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- CONFIGURATION ---
st.set_page_config(page_title="RV AI PRO", page_icon="https://i.postimg.cc/5y14PWfB/RV-AI.jpg", layout="wide")
init_db()

# Custom CSS for Open WebUI Look
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #171717; border-right: 1px solid #333; }
    .main { background-color: #212121; color: #ececec; }
    .stTextInput > div > div > input { background-color: #303030; color: white; border-radius: 10px; }
    .chat-bubble { padding: 20px; border-radius: 15px; margin: 10px 0; line-height: 1.6; }
    .user-bubble { background-color: #303030; }
    .ai-bubble { background-color: transparent; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #3c3d3e; color: white; border: none; }
    .stButton>button:hover { background-color: #4e4f50; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("https://i.postimg.cc/5y14PWfB/RV-AI.jpg", width=100)
        st.title("RV AI PRO Login")
        auth_mode = st.tabs(["Login", "Register"])
        
        with auth_mode[0]:
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            if st.button("Login"):
                conn = sqlite3.connect('rv_ai_users.db')
                c = conn.cursor()
                c.execute('SELECT password FROM users WHERE username = ?', (username,))
                data = c.fetchone()
                if data and check_hashes(password, data[0]):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("වැරදි පරිශීලක නාමයක් හෝ මුරපදයක්")

        with auth_mode[1]:
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type='password')
            if st.button("Sign Up"):
                conn = sqlite3.connect('rv_ai_users.db')
                c = conn.cursor()
                try:
                    c.execute('INSERT INTO users(username, password) VALUES (?,?)', (new_user, make_hashes(new_pass)))
                    conn.commit()
                    st.success("ගිණුම සාර්ථකව සෑදුවා! දැන් Login වන්න.")
                except:
                    st.error("මෙම නම දැනටමත් භාවිතයේ ඇත.")
    st.stop()

# --- MAIN INTERFACE (Open WebUI Style) ---
with st.sidebar:
    st.image("https://i.postimg.cc/5y14PWfB/RV-AI.jpg", width=50)
    st.title("RV AI PRO")
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.subheader("Chat History")
    # මෙතැනට SQLite වලින් පරණ චැට් ලිස්ට් එකක් ගත හැක (දැනට සරලව තබා ඇත)
    
    st.spacer = st.container()
    with st.container():
        st.write(f"👤 {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- CHAT ENGINE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Message RV AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            url = "http://65.108.212.204:11434/api/generate"
            payload = {"model": "phi3", "prompt": prompt, "stream": False}
            
            res = requests.post(url, json=payload, timeout=60)
            if res.status_code == 200:
                full_response = res.json().get("response", "")
                response_placeholder.markdown(full_response)
            else:
                st.error("Ollama සර්වර් එකෙන් වැරදි ප්‍රතිචාරයක් ආවා.")
        except Exception as e:
            st.error("සම්බන්ධතාවය බිඳ වැටුණා. සර්වර් එක චෙක් කරන්න.")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
