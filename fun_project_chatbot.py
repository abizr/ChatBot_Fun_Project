import io

import speech_recognition as sr
import streamlit as st
from audio_recorder_streamlit import audio_recorder as audiorecorder

from core import DocumentIngestor, OpenRouterClient, OpenRouterError, RagConfig, RagPipeline
from core.utils import run_async, truncate_text

# ---------------------------------------------------------------------------
# Global services & configuration
# ---------------------------------------------------------------------------

DOCUMENT_INGESTOR = DocumentIngestor(chunk_size=640, chunk_overlap=160)
RAG_PIPELINE = RagPipeline(config=RagConfig(top_k=4, max_context_chars=2200))

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True


def speech_to_text(audio_data, language="en-US"):
    """
    Convert microphone recordings (WAV bytes) to text via Google's free API.
    """
    if not audio_data:
        return ""

    audio_bytes = audio_data if isinstance(audio_data, (bytes, bytearray)) else audio_data.tobytes()
    buffer = io.BytesIO(audio_bytes)
    try:
        with sr.AudioFile(buffer) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.record(source)
    except Exception as exc:
        st.error(f"Could not read audio stream: {exc}")
        return ""

    try:
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        st.warning("Sorry, I could not understand that audio. Please try again or reduce background noise.")
    except sr.RequestError as exc:
        st.error(f"Speech-to-text service is unavailable: {exc}")
    return ""


def ingest_document(uploaded_file):
    """Parse uploaded files, create FAISS index, and store diagnostics in session state."""
    file_bytes = uploaded_file.getvalue()
    doc_id = RAG_PIPELINE.make_doc_id(file_bytes, uploaded_file.name)
    state = st.session_state

    if state.get("active_doc_id") == doc_id and state.get("doc_bundle"):
        return state["doc_bundle"].text

    try:
        bundle = DOCUMENT_INGESTOR.ingest(uploaded_file.name, file_bytes)
        state["doc_bundle"] = bundle
        state["active_doc_id"] = doc_id
        state["doc_error"] = None
        state["doc_ingest_messages"] = bundle.diagnostics or ["Document ingested successfully."]
        state["rag_ready"] = False

        if bundle.chunks:
            RAG_PIPELINE.upsert(doc_id, bundle.chunks, metadata={"file_name": uploaded_file.name})
            state["rag_ready"] = True
            state["doc_ingest_messages"].append(f"Indexed {len(bundle.chunks)} chunks for retrieval.")
        else:
            state["doc_ingest_messages"].append("Document contained no readable text; retrieval disabled.")
    except Exception as exc:
        state["doc_bundle"] = None
        state["doc_error"] = str(exc)
        state["doc_ingest_messages"] = [f"Document ingestion failed: {exc}"]
        state["active_doc_id"] = None
        state["rag_ready"] = False

    return state["doc_bundle"].text if state.get("doc_bundle") else ""


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Fun Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="text-align:center; margin-bottom: 1.5rem;">
        <h1 style="margin-bottom:0.2rem;">🤖 AI Fun Chatbot</h1>
        <p style="color:#555; font-size:1.1rem; margin-top:0;">Chat with AI, upload documents, or use your voice. Now powered by FAISS RAG.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

default_state = {
    "chat_history": [],
    "internal_pending_user_input": None,
    "doc_bundle": None,
    "doc_error": None,
    "doc_ingest_messages": [],
    "active_doc_id": None,
    "rag_ready": False,
}
for key, value in default_state.items():
    st.session_state.setdefault(key, value)


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("Settings & Inputs")
    st.markdown("---")
    st.header("API & Model")
    api_key = st.text_input("OpenRouter API Key", type="password")
    model = st.selectbox(
        "Select AI Model",
        options=[
            "gpt-4",
            "anthropic/claude-2",
            "deepseek/deepseek-chat-v3-0324:free",
            "qwen/qwen3-235b-a22b:free",
        ],
        index=0,
    )
    st.markdown("---")
    st.header("Document & Voice")
    uploaded_file = st.file_uploader("Upload PDF or DOCX file", type=["pdf", "docx"])
    audio_bytes = audiorecorder("Start Recording", "Stop Recording")
    st.markdown("### Image & Video Upload")
    uploaded_image = st.file_uploader(
        "Upload an image", type=["png", "jpg", "jpeg", "bmp", "gif"], key="image_uploader"
    )
    uploaded_video = st.file_uploader(
        "Upload a video", type=["mp4", "mov", "avi", "webm"], key="video_uploader"
    )

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []

    if uploaded_file is None and st.session_state.get("doc_bundle"):
        if st.button("Remove cached document"):
            st.session_state["doc_bundle"] = None
            st.session_state["doc_error"] = None
            st.session_state["doc_ingest_messages"] = []
            st.session_state["active_doc_id"] = None
            st.session_state["rag_ready"] = False

    if uploaded_file is not None:
        if st.session_state.get("doc_error"):
            st.error(f"Document error: {st.session_state['doc_error']}")
        else:
            bundle = st.session_state.get("doc_bundle")
            if bundle:
                st.success(
                    f"Chunks ready: {bundle.metadata.get('num_chunks', 0)} "
                    f"(Context {'enabled' if st.session_state.get('rag_ready') else 'pending'})"
                )

    st.markdown("---")
    st.markdown(
        """
        <div style="background-color:#e8f0fe; border-left:4px solid #4285f4; padding:1em; border-radius:6px; margin-bottom:1em;">
        <b>How to use:</b><br>
        - Type or record your message.<br>
        - Upload a document for retrieval-augmented answers.<br>
        - Chat history stays local.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<small>Made with ❤️ using Streamlit</small>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Document ingestion + diagnostics
# ---------------------------------------------------------------------------

file_text = ""
if uploaded_file is not None:
    file_text = ingest_document(uploaded_file)
elif st.session_state.get("doc_bundle"):
    file_text = st.session_state["doc_bundle"].text

doc_error = st.session_state.get("doc_error")
doc_messages = st.session_state.get("doc_ingest_messages", [])
if doc_error:
    st.error(f"Document upload failed: {doc_error}")
elif doc_messages and st.session_state.get("doc_bundle"):
    with st.expander("Document ingestion details", expanded=False):
        for msg in doc_messages:
            st.write(f"- {msg}")


# ---------------------------------------------------------------------------
# Chat transcript
# ---------------------------------------------------------------------------

st.markdown('<div class="chat-container" style="max-height: 60vh; overflow-y: auto;">', unsafe_allow_html=True)
for i, chat in enumerate(st.session_state.chat_history):
    role_class = "user-message" if chat["role"] == "user" else "bot-message"
    st.markdown(f'<div class="chat-message {role_class}">{chat["content"]}</div>', unsafe_allow_html=True)
    if i < len(st.session_state.chat_history) - 1:
        st.markdown('<hr style="border: none; border-top: 1px solid #eee; margin: 8px 0;" />', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

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
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Speech-to-text
# ---------------------------------------------------------------------------

if audio_bytes:
    st.markdown("**Transcribing audio...**")
    transcribed_text = speech_to_text(audio_bytes)
    if transcribed_text:
        st.markdown(f"**You said:** {transcribed_text}")
        st.session_state["internal_pending_user_input"] = transcribed_text
    else:
        st.markdown("**Could not transcribe audio. Please try again or type your message.**")


# ---------------------------------------------------------------------------
# Media previews
# ---------------------------------------------------------------------------

if uploaded_image is not None:
    st.markdown("<b>Image Preview:</b>", unsafe_allow_html=True)
    st.image(uploaded_image, use_column_width=True)
if uploaded_video is not None:
    st.markdown("<b>Video Preview:</b>", unsafe_allow_html=True)
    st.video(uploaded_video)


# ---------------------------------------------------------------------------
# LLM call with RAG context
# ---------------------------------------------------------------------------

if st.session_state.get("internal_pending_user_input"):
    with st.spinner("AI is thinking..."):
        pending_user_input = st.session_state["internal_pending_user_input"]
        if not api_key:
            st.error("Please enter your OpenRouter API key in the sidebar.")
        else:
            messages = [
                {
                    "role": "system",
                    "content": "You are AI Fun Chatbot. Keep answers concise, friendly, and cite document snippets when used.",
                }
            ]

            rag_context = ""
            doc_id = st.session_state.get("active_doc_id")
            if doc_id and st.session_state.get("rag_ready"):
                rag_context = RAG_PIPELINE.build_context_prompt(
                    pending_user_input,
                    doc_id=doc_id,
                    top_k=RAG_PIPELINE.config.top_k,
                )
            elif file_text:
                rag_context = f"Document context (fallback):\n{truncate_text(file_text, max_chars=1800)}"

            if rag_context:
                messages.append({"role": "system", "content": rag_context})

            for chat in st.session_state.chat_history:
                messages.append({"role": chat["role"], "content": chat["content"]})
            messages.append({"role": "user", "content": pending_user_input})

            try:
                client = OpenRouterClient(api_key=api_key, model=model)
                response = run_async(client.chat(messages, max_tokens=512))
            except OpenRouterError as exc:
                response = f"Error: {exc}"
            except Exception as exc:
                response = f"Unexpected error talking to OpenRouter: {exc}"

            st.session_state.chat_history.append({"role": "user", "content": pending_user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": response})

        st.session_state["internal_pending_user_input"] = None
        st.rerun()


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="footer" style="background:#f0f2f6; padding:1rem 0; border-radius:8px;">'
    "Developer by Abizar Al Gifari Rahman 😎 © 2025"
    "</div>",
    unsafe_allow_html=True,
)
