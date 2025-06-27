import asyncio
import aiohttp
import streamlit as st
import io
from docx import Document
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder as audiorecorder

# ---------------------------
# Helper functions for document processing
# ---------------------------

def extract_text_from_pdf(file_bytes):
    # Extract text directly from PDF file bytes
    # This function reads the PDF and extracts text from each page
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_bytes):
    # Extract text from DOCX file bytes
    # This function loads the DOCX document and concatenates all paragraphs
    doc = Document(io.BytesIO(file_bytes))
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def extract_text_from_pdf_with_ocr(file_bytes):
    # OCR is not available on Streamlit Cloud due to missing system binaries
    st.warning("OCR for scanned PDFs is not available on Streamlit Cloud. Please use a PDF with selectable text.")
    return ""

# ---------------------------
# Speech-to-text function using speech_recognition
# ---------------------------

def speech_to_text(audio_data):
    # Speech-to-text is not available on Streamlit Cloud due to missing system binaries
    st.warning("Speech-to-text is not available on Streamlit Cloud. Please type your message instead.")
    return ""

# ---------------------------
# Asynchronous function to call OpenRouter API
# ---------------------------

async def call_openrouter_api(messages, model, api_key, max_tokens=512):
    # Asynchronously send chat messages to OpenRouter API and get response
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data['choices'][0]['message']['content']
            else:
                error_message = await resp.text()
                # User-friendly error for 402
                if resp.status == 402:
                    return "Error: Insufficient credits or request too large. Please reduce your message size or upgrade your OpenRouter account."
                return f"Error: {resp.status}, Message: {error_message}"

     

# ---------------------------
# Streamlit UI and main logic
# ---------------------------

# Set page configuration with modern UI elements
st.set_page_config(
    page_title="AI Fun Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Google Fonts and custom CSS for modern styling
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f5f7fa;
            color: #333333;
        }
        .chat-container {
            max-width: 900px;
            margin: auto;
            padding: 1rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .chat-message {
            padding: 10px 15px;
            border-radius: 20px;
            margin-bottom: 10px;
            max-width: 75%;
            word-wrap: break-word;
            font-size: 1rem;
            line-height: 1.4;
        }
        .user-message {
            background-color: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            background-color: #e4e6eb;
            color: #333;
            margin-right: auto;
            text-align: left;
        }
        .sidebar .stButton>button {
            width: 100%;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            color: #888;
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)

# Header with branding and description
st.markdown("""
    <div style="text-align:center; margin-bottom: 1.5rem;">
        <h1 style="margin-bottom:0.2rem;">🤖 AI Fun Chatbot</h1>
        <p style="color:#555; font-size:1.1rem; margin-top:0;">Chat with AI, upload documents, or use your voice. Powered by OpenRouter.</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for settings and inputs
with st.sidebar:
    st.title("Settings & Inputs")
    st.markdown("---")
    st.header("API & Model")
    api_key = st.text_input("OpenRouter API Key", type="password")
    model = st.selectbox(
        "Select AI Model",
        options=["gpt-4", "anthropic/claude-2"],
        index=0
    )
    st.markdown("---")
    st.header("Document & Voice")
    uploaded_file = st.file_uploader("Upload PDF or DOCX file", type=["pdf", "docx"])
    st.markdown("### Record your voice message")
    audio_bytes = audiorecorder("Start Recording", "Stop Recording")
    st.markdown("---")
    # New: Image & Video Upload Section
    st.header("Image & Video Upload")
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "bmp", "gif"], key="image_uploader")
    uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "webm"], key="video_uploader")
    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
    st.markdown("---")
    # Replace st.info with styled st.markdown for HTML info box
    st.markdown("""
    <div style="background-color:#e8f0fe; border-left:4px solid #4285f4; padding:1em; border-radius:6px; margin-bottom:1em;">
    <b>How to use:</b><br>
    - Type or record your message.<br>
    - Upload a document for context.<br>
    - Your chat history is private and local.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<small>Made with ❤️ using Streamlit</small>", unsafe_allow_html=True)

# Extract text from uploaded file if any
file_text = ""
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    if uploaded_file.type == "application/pdf":
        # Try direct text extraction first
        file_text = extract_text_from_pdf(file_bytes)
        if not file_text.strip():
            # If no text found, use OCR
            file_text = extract_text_from_pdf_with_ocr(file_bytes)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_text = extract_text_from_docx(file_bytes)

# Display main chat container (scrollable)
st.markdown('<div class="chat-container" style="max-height: 60vh; overflow-y: auto;">', unsafe_allow_html=True)

# Display chat history with styled chat bubbles and separator
for i, chat in enumerate(st.session_state.chat_history):
    if chat["role"] == "user":
        st.markdown(f'<div class="chat-message user-message">{chat["content"]}</div>', unsafe_allow_html=True)
    elif chat["role"] == "assistant":
        st.markdown(f'<div class="chat-message bot-message">{chat["content"]}</div>', unsafe_allow_html=True)
    # Add a subtle separator after each message pair
    if i < len(st.session_state.chat_history) - 1:
        st.markdown('<hr style="border: none; border-top: 1px solid #eee; margin: 8px 0;" />', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input for user message (requires Streamlit >=1.25)
if "internal_pending_user_input" not in st.session_state:
    st.session_state["internal_pending_user_input"] = None

user_input = None
if hasattr(st, "chat_input"):
    user_input = st.chat_input("Type your message here...", key="pending_user_input")
    if user_input:
        st.session_state["internal_pending_user_input"] = user_input
else:
    st.markdown(
        """
        <style>
        .fallback-input {
            position: fixed;
            bottom: 30px;
            left: 0;
            width: 100vw;
            background: #fff;
            padding: 1rem 2rem;
            box-shadow: 0 -2px 8px rgba(0,0,0,0.04);
            z-index: 9999;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container():
        st.markdown('<div class="fallback-input">', unsafe_allow_html=True)
        fallback_input = st.text_input("Type your message here...", key="pending_user_input")
        if fallback_input:
            st.session_state["internal_pending_user_input"] = fallback_input
        st.markdown('</div>', unsafe_allow_html=True)

# If audio recorded, convert to text
if audio_bytes:
    audio_data = audio_bytes.tobytes()
    st.markdown("**Transcribing audio...**")
    transcribed_text = speech_to_text(audio_data)
    if transcribed_text:
        st.markdown(f"**You said:** {transcribed_text}")
        st.session_state["internal_pending_user_input"] = transcribed_text
    else:
        st.markdown("**Could not transcribe audio. Please try again or type your message.**")

# Display preview of uploaded image or video
if uploaded_image is not None:
    st.markdown("<b>Image Preview:</b>", unsafe_allow_html=True)
    st.image(uploaded_image, use_column_width=True)
if uploaded_video is not None:
    st.markdown("<b>Video Preview:</b>", unsafe_allow_html=True)
    st.video(uploaded_video)

# Show a spinner while waiting for a response
if st.session_state.get("internal_pending_user_input"):
    with st.spinner("AI is thinking..."):
        user_input = st.session_state["internal_pending_user_input"]
        if not api_key:
            st.error("Please enter your OpenRouter API key in the sidebar.")
        else:
            # Prepare messages for API call
            messages = []
            # Add system prompt with file context if available
            if file_text.strip():
                messages.append({"role": "system", "content": f"Context from uploaded document:\n{file_text}"})
            # Add chat history
            for chat in st.session_state.chat_history:
                messages.append({"role": chat["role"], "content": chat["content"]})
            # Add current user input
            messages.append({"role": "user", "content": user_input})

            # Call OpenRouter API asynchronously and get response
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            response = loop.run_until_complete(call_openrouter_api(messages, model, api_key, max_tokens=512))

            # Update chat history with user input and bot response
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        # Clear pending input so it doesn't get processed again
        st.session_state["internal_pending_user_input"] = None
        st.rerun()

# Footer
st.markdown('<div class="footer" style="background:#f0f2f6; padding:1rem 0; border-radius:8px;">Developer by Abizar Al Gifari Rahman 😎 &copy; 2025</div>', unsafe_allow_html=True)
