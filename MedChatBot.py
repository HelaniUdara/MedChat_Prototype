import streamlit as st
import requests
from streamlit_chat import message
import json
import base64
import uuid


# ---------------------------
# HELPER FUNCTION FOR IMAGES
# ---------------------------

def get_base64_image(image_path):
    """Convert local image to base64 string"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Image not found: {image_path}")
        return None


# ---------------------------
# CONFIG & PAGE SETUP
# ---------------------------

st.set_page_config(
    page_title="MedSeek AI Receptionist",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for ChatGPT-like UI
st.markdown("""
    <style>
    /* Main background */
    .main {
        background-color: #111111;
    }

    /* Center the chat container */
    .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header styling */
    h1 {
        text-align: left;
        margin-bottom: 0.5rem;
        color: #FFFFFF !important;
    }

    /* Typing indicator styling */
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 15px 20px;
        border-radius: 18px;
        width: fit-content;
        margin: 10px 0;
    }

    .typing-indicator span {
        height: 8px;
        width: 8px;
        background-color: #6B7280;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: typing 1.4s infinite;
    }

    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }

    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }

    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
        }
        30% {
            transform: translateY(-10px);
        }
    }

    /* Input box styling */
    .stTextInput input {
        border-radius: 24px;
        border: 1.5px solid #374151;
        padding: 14px 20px;
        font-size: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        background-color: #1F2937 !important;
        color: white !important;
    }

    .stTextInput input:focus {
        border-color: #4F46E5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.3);
        background-color: #1F2937 !important;
    }

    .stTextInput input::placeholder {
        color: #9CA3AF;
    }

    /* Send button styling */
    .stButton > button {
        background-color: #06B6D4;
        color: white;
        border: none;
        border-radius: 50%;
        width: 45px;
        height: 45px;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 18px;
        margin-top: 0;
    }

    .stButton > button:hover {
        background-color: #0891B2;
        transform: scale(1.05);
    }

    .stButton > button:active {
        transform: scale(0.95);
    }

    /* Fix column layout for input - remove gaps */
    div[data-testid="column"] {
        padding: 0 5px !important;
    }

    /* Align button column vertically */
    div[data-testid="column"]:last-child {
        display: flex;
        align-items: flex-end;
    }

    /* Critical alert styling */
    .critical-alert {
        padding: 12px 18px;
        background-color: #FEE2E2;
        border-left: 6px solid #EF4444;
        border-radius: 8px;
        font-weight: 600;
        color: #991B1B;
        margin-bottom: 1rem;
        text-align: center;
    }

    .error-alert {
        padding: 12px 18px;
        background-color: #FEF3C7;
        border-left: 6px solid #F59E0B;
        border-radius: 8px;
        color: #92400E;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Chat messages spacing */
    .stChatMessage {
        margin-bottom: 1rem;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hide default spinner */
    .stSpinner {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "sessionId" not in st.session_state:
    st.session_state.sessionId = uuid.uuid4().hex

if "messages" not in st.session_state:
    st.session_state.messages = []

if "critical_detected" not in st.session_state:
    st.session_state.critical_detected = False

if "last_error" not in st.session_state:
    st.session_state.last_error = None

if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

# ---------------------------
# HEADER
# ---------------------------

st.title("🩺 MedSeek AI Receptionist")
st.divider()

# ---------------------------
# ALERTS
# ---------------------------

if st.session_state.critical_detected:
    st.markdown(
        '<div class="critical-alert">⚠️ Critical condition detected — emergency guidance was provided.</div>',
        unsafe_allow_html=True
    )

if st.session_state.last_error:
    st.markdown(
        f'<div class="error-alert">⚠️ {st.session_state.last_error}</div>',
        unsafe_allow_html=True
    )

# ---------------------------
# CHAT CONTAINER
# ---------------------------

chat_container = st.container()

# Load avatar images (change these filenames to match your actual files)
user_avatar_base64 = get_base64_image("User.png")  # Change to your user image filename
ai_avatar_base64 = get_base64_image("Medical_Assistant.png")  # Change to your AI image filename

# Create data URIs for the avatars
user_avatar = f"data:image/png;base64,{user_avatar_base64}" if user_avatar_base64 else None
ai_avatar = f"data:image/png;base64,{ai_avatar_base64}" if ai_avatar_base64 else None

with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            # User message with custom image
            message(
                msg["content"],
                is_user=True,
                key=f"msg_{i}",
                # avatar=user_avatar  # Use your custom user image
            )
        else:
            # AI assistant message with custom image
            message(
                msg["content"],
                is_user=False,
                key=f"msg_{i}",
                # avatar=ai_avatar  # Use your custom AI image
            )

# Show typing indicator when agent is processing
if st.session_state.is_typing:
    st.markdown(
        '<div class="typing-indicator"><span></span><span></span><span></span></div>',
        unsafe_allow_html=True
    )

# ---------------------------
# INPUT BOX WITH SEND ICON
# ---------------------------

# Add some spacing before input
st.markdown("<br>", unsafe_allow_html=True)

# Create columns for input and button - better ratio
input_col, button_col = st.columns([0.92, 0.08])

with input_col:
    user_input = st.text_input(
        "Message",
        placeholder="Talk to your AI Medical Receptionist...",
        key="user_input",
        label_visibility="collapsed"
    )

with button_col:
    send_button = st.button("➤", key="send_btn", help="Send message")


# ---------------------------
# N8N API CALL FUNCTION
# ---------------------------

def call_n8n_agent(prompt):
    """
    Call the N8N webhook
    """
    # webhook_url = "https://n8n.fexcon.com.au/webhook/06b637e2-5bb9-4bbb-bdff-b86b01106de7"

    webhook_url = "https://n8n.fexcon.com.au/webhook/b3e70480-50d1-4a94-936a-ac94bc94445d/chat"
    try:
        payload = {
            "sessionId": st.session_state.sessionId,
            "action": "sendMessage",
            "chatInput": prompt
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(
            url=webhook_url,
            json=payload,
            headers=headers,
            timeout=60
        )

        # Handle different status codes
        if response.status_code == 500:
            try:
                error_json = response.json()
                error_message = error_json.get("message", "Internal server error")

                if "Unused Respond to Webhook" in error_message:
                    return {
                        "reply": "⚠️ The workflow is not configured correctly. Please check the n8n workflow.",
                        "error": True
                    }
                else:
                    return {
                        "reply": f"Workflow error: {error_message}",
                        "error": True
                    }
            except:
                return {
                    "reply": "The workflow encountered an error. Please check n8n.",
                    "error": True
                }

        if response.status_code != 200:
            return {
                "reply": f"Server returned error code {response.status_code}.",
                "error": True
            }

        # Parse successful response
        try:
            json_response = response.json()

            # Handle different response formats
            if isinstance(json_response, dict):
                if "reply" in json_response:
                    return json_response
                elif "output" in json_response:
                    return {"reply": json_response["output"]}
                elif "message" in json_response:
                    return {"reply": json_response["message"]}
                else:
                    # Return first available text field
                    for key, value in json_response.items():
                        if isinstance(value, str) and len(value) > 0:
                            return {"reply": value}
                    return {"reply": str(json_response)}
            else:
                return {"reply": str(json_response)}

        except json.JSONDecodeError:
            return {"reply": response.text}

    except requests.exceptions.Timeout:
        return {
            "reply": "Request timed out. Please try again.",
            "error": True
        }

    except requests.exceptions.ConnectionError:
        return {
            "reply": "Could not connect to the medical assistant. Please check your connection.",
            "error": True
        }

    except Exception as e:
        return {
            "reply": f"An error occurred: {str(e)}",
            "error": True
        }


# ---------------------------
# MAIN CHAT LOGIC
# ---------------------------

if send_button and user_input:
    # Clear previous errors
    st.session_state.last_error = None

    # Store the user input before clearing
    user_message = user_input

    # Save user message immediately
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Set typing indicator
    st.session_state.is_typing = True

    # Force rerun to show user message and typing indicator
    st.rerun()

# Handle API call after rerun (when typing indicator is visible)
if st.session_state.is_typing:
    # Get the last user message
    last_message = st.session_state.messages[-1]["content"]

    # Call your N8N workflow
    bot_result = call_n8n_agent(last_message)

    # Check for errors
    if bot_result.get("error"):
        st.session_state.last_error = bot_result.get("reply")

    # Extract agent reply
    agent_reply = bot_result.get("reply", "I couldn't process the request.")

    # Detect critical warning in agent response
    if "call 111" in agent_reply.lower() or "emergency" in agent_reply.lower():
        st.session_state.critical_detected = True

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": agent_reply})

    # Turn off typing indicator
    st.session_state.is_typing = False


    st.rerun()






