import streamlit as st
import requests
import time
import logging

# logging to store messages
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# chatbot avatar GIF 
col1, col2 = st.columns((0.1, 0.9)) 

with col1:
    st.image("chatbot_avatar.gif.gif", width=60) 

with col2:
    st.title("Calm Chatbot") 

# API Endpoint
API_URL = "http://127.0.0.1:5001/chat"  

# Styling
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] { display: none; }

        /* Background Gradient Animation */
        @keyframes gradientAnimation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .stApp {
            background: linear-gradient(-45deg, #d4eaf7, #e3d7ff, #f5e6cc, #d3f3e3);
            background-size: 400% 400%;
            animation: gradientAnimation 15s ease infinite;
        }

         /* Chat Bubble Styling */
        .chat-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
        .chat-bubble {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 20px;
            margin-bottom: 10px;
            word-wrap: break-word;
            display: inline-block;
        }
        .user-bubble {
            background-color: #4CAF50;
            color: white;
            align-self: flex-end;
        }
        .bot-bubble {
            background-color: #f1f1f1;
            color: black;
            align-self: flex-start;
        }
        /* Floating Bubbles */
        .bubble {
            position: absolute;
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            opacity: 0.6;
            animation: floatUp 10s infinite ease-in;
        }

        @keyframes floatUp {
            0% { transform: translateY(100vh); opacity: 0.4; }
            100% { transform: translateY(-10vh); opacity: 0; }
        }

        /* Bubble Container */
        .bubble-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100vh;
            pointer-events: none;
            overflow: hidden;
        }

        /* Fixed Chat Input */
        .chat-input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: white;
            padding: 10px;
            box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: center;
        }

        .chat-input {
            width: 90%;
            max-width: 600px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 16px;
        }

        /* Emergency Contacts */
        .emergency-contacts {
            position: fixed;
            bottom: 50px;
            right: 20px;
            font-size: 14px;
            color: #333;
            text-align: right;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Bubbles
def create_bubbles():
    bubble_styles = "".join(
        f'<div class="bubble" style="width:{size}px; height:{size}px; left:{left}%; animation-duration:{duration}s;"></div>'
        for size, left, duration in [(20, 10, 8), (40, 50, 12), (30, 80, 10), (25, 20, 14), (35, 60, 9)]
    )
    st.markdown(f'<div class="bubble-container">{bubble_styles}</div>', unsafe_allow_html=True)

create_bubbles()

# user authentication
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Please log in first.")
    st.stop()

st.title("Calm Chatbot")
st.write("Start chatting with our AI-powered assistant. Your messages are private and secure.")


# chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# send message
def send_message():
    user_input = st.session_state.get("user_input", "").strip()

    if user_input: 
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Typing..."):
            time.sleep(1.5)  # typing delay

        try:
            API_URL = "http://127.0.0.1:5001/chat"  
            response = requests.post(API_URL, json={"message": user_input})
            logging.debug("API Response: %s", response.json()) 


            if response.status_code == 200:
                bot_response = response.json().get("response", "I'm not sure how to respond.")
            else:
                bot_response = f"❌ Error {response.status_code}: {response.text}"

        except Exception as e:
            bot_response = f"❌ Error: {e}"

        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

        # Clear input box
        st.session_state.pop("user_input", None)

        # Display chat messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    bubble_class = "user-bubble" if message["role"] == "user" else "bot-bubble"
    st.markdown(f'<div class="chat-bubble {bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

user_input = st.text_input("Type your message here...", key="user_input", on_change=send_message)
if user_input:
    send_message()

# Logout Button
if st.button("Logout"):
    st.session_state["authenticated"] = False
    st.success("Logged out successfully! Redirecting...")
    time.sleep(2)
    st.rerun()

# Emergency Contacts
st.markdown(
    '<div class="emergency-contacts">'
    'Emergency Contacts:<br>'
    'Mental Health Support: 123-456-7890<br>'
    'Suicide Prevention: 987-654-3210<br>'
    'Crisis Helpline: 555-777-9999'
    '</div>',
    unsafe_allow_html=True
)
