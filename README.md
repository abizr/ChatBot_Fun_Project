# ChatBot Fun Project Skill Academy Pro
# This second project is a fun step toward completing the AI Python Bootcamp

========================================================================================================================================================================================


## AI Fun Chatbot <br>
Table of Contents: <br>
●	Project Overview<br>
●	Installation Instructions<br>
●	Usage Guidelines<br>
●	Features<br>
●	Required Dependencies<br>
●	Running the Application<br>

## Project Overview
The AI Fun Chatbot is an innovative Streamlit-based application designed to provide an interactive AI chatbot experience enriched with advanced document processing and speech-to-text capabilities. This project integrates multiple cutting-edge technologies to allow users to interact with an AI assistant that can understand and process various document formats such as PDF and DOCX, as well as convert spoken audio into text for seamless communication.
This chatbot leverages asynchronous API calls to OpenRouter's AI models, enabling real-time, intelligent conversations. It supports direct text extraction from documents, optical character recognition (OCR) for scanned PDFs, and speech recognition for audio inputs, making it a versatile tool for users who want to interact with AI in multiple modalities. The application is built with a modern, user-friendly interface using Streamlit, enhanced with custom styling and Google Fonts for an appealing visual experience.<br>
The project is ideal for developers, researchers, and enthusiasts interested in AI-driven conversational agents, document analysis, and speech processing technologies. It serves as a comprehensive example of integrating various Python libraries and APIs to create a sophisticated, multi-functional chatbot application.<br>

## Refactored Project Architecture
- `fun_project_chatbot.py` now focuses purely on Streamlit UI + orchestration.
- `core/doc_ingest.py` wraps PDF/DOCX parsing, OCR fallbacks, and text chunking (640 token windows with 160-token overlaps).
- `core/rag.py` persists chunks + embeddings into `data/rag_cache/` using FAISS + NumPy so context survives reruns.
- `core/llm_client.py` centralizes OpenRouter calls with friendly error handling.
- `core/utils.py` contains shared helpers (token chunker, hashing, async runner).

```
chatbot_project/
├─ fun_project_chatbot.py         # Streamlit experience + prompt assembly
├─ core/
│  ├─ doc_ingest.py               # Upload parsing + OCR diagnostics
│  ├─ rag.py                      # FAISS index management + context windows
│  ├─ llm_client.py               # OpenRouter wrapper (async)
│  ├─ utils.py                    # common helpers
│  └─ __init__.py
└─ data/rag_cache/                # auto-created FAISS + metadata artifacts
```

## Minimal FAISS RAG workflow
1. **Document upload:** `DocumentIngestor` extracts native PDF/DOCX text and only triggers OCR when selectable text is missing. Missing Poppler/Tesseract binaries are reported but no longer crash the app.
2. **Chunking:** Extracted text is split into ~640-token chunks with 160-token overlap (tiktoken when available, word fallback otherwise) to preserve context continuity.
3. **Embedding + storage:** `RagPipeline` encodes chunks via `sentence-transformers` (`all-MiniLM-L6-v2`), saves the FAISS index (`index.faiss`), embeddings (`embeddings.npy`), and metadata (`metadata.json`) under a stable hash of the file bytes.
4. **Retrieval:** For every user turn we fetch the top-k (default 4) chunks, build a bounded context window (~2.2k chars), and append it as a lightweight system message—keeping the base system prompt small.
5. **Fallback:** If FAISS/embeddings are unavailable, the chatbot falls back to a truncated plain-text context so responses still work (just without semantic search quality).

## Document upload & OCR troubleshooting
- Live ingestion diagnostics are surfaced via an expandable panel in the main UI and via sidebar badges (success/error).
- Common failure cases (missing poppler binaries, pytesseract not installed, zero-text PDFs) are captured without throwing, ensuring uploads always complete.
- To enable OCR on Streamlit Cloud ensure `packages.txt` lists `tesseract-ocr` and `poppler-utils`, or disable OCR via `DocumentIngestor(enable_ocr=False)` if your deployment cannot install system packages.

## Installation Instructions<br>
To get started with the AI Fun Chatbot, follow these detailed installation steps to set up the environment and dependencies required for the application to run smoothly.<br>

## Prerequisites<br>
●	Python 3.8 or higher installed on your system.<br>
●	A stable internet connection for downloading dependencies and accessing the OpenRouter API.<br>
●	An API key from OpenRouter to enable AI model interactions.<br>

## Step-by-Step Installation <br>
1.	Clone the Repository<br>
2.	Begin by cloning the project repository to your local machine:<br>
git clone https://github.com/yourusername/ai-fun-chatbot.git cd ai-fun-chatbot <br>
3.	Create a Virtual Environment <br>
4.	It is highly recommended to use a virtual environment to manage dependencies:<br>
python -m venv venv source venv/bin/activate  # On Windows use: venv\Scripts\activate <br>
5.	Install Required Dependencies <br>
6.	Install all necessary Python packages using pip and the provided requirements.txt file:<br>
pip install -r requirements.txt <br>
7.	Set Up Environment Variables <br>
8.	Export your OpenRouter API key as an environment variable to authenticate API requests: <br>
export OPENROUTER_API_KEY="your_api_key_here"  # On Windows use: set OPENROUTER_API_KEY=your_api_key_here <br>
9.	Verify Installation <br>
10.	Confirm that all dependencies are installed correctly by running: <br>
python fun_project_chatbot.py --help <br>
11.	This should display usage information without errors. <br>

## Streamlit Cloud Deployment (Recommended)
Follow these steps to deploy a public app directly from GitHub:

- Repo files required:
  - `requirements.txt` (Python deps; do NOT include `asyncio` — it’s part of Python)
  - `runtime.txt` with `3.10` to match your local Python version
  - `packages.txt` (optional) with `tesseract-ocr`, `poppler-utils`, and `ffmpeg` if you want OCR/audio features

- Create app in Streamlit Cloud:
  - Connect your GitHub repo and branch
  - Main file path: `fun_project_chatbot.py`
  - Python version: picked from `runtime.txt`
  - Secrets: add `OPENROUTER_API_KEY`

- First deploy may take a few minutes while dependencies install.

### Troubleshooting Installer Errors
If you see “Installer returned a non-zero exit code” during deployment:

- Remove `asyncio` from `requirements.txt` (it’s a stdlib module; backports break on Python 3.10+)
- Ensure your repo contains `runtime.txt` with `3.10`
- If you enabled OCR, make sure `packages.txt` includes `tesseract-ocr` and `poppler-utils`
- Open the app logs in Streamlit Cloud to see the specific package that failed to install

### OCR and Speech Notes
- OCR for scanned PDFs requires system binaries. With `packages.txt` (above), the app will automatically use OCR when available; otherwise it falls back gracefully.
- Speech-to-text attempts basic recognition from WAV bytes using `SpeechRecognition`. If the audio format or system tools are missing, the app will show a friendly message and continue normally.

## Usage Guidelines <br>
The AI Fun Chatbot is designed for ease of use, allowing users to interact with the AI through a web interface powered by Streamlit. Below are comprehensive instructions on how to use the application effectively.
Launching the Application <br>
Run the Streamlit app with the following command:<br>
streamlit run fun_project_chatbot.py <br>
This will start a local web server and open the chatbot interface in your default browser.<br>
Interacting with the Chatbot <br>
●	Text Chat: Type your messages directly into the chat input box to converse with the AI.<br>
●	Document Upload: Upload PDF or DOCX files to have the chatbot extract and understand the content. The chatbot can process both text-based PDFs and scanned documents using OCR.<br>
●	Speech Input: Record audio messages using the integrated audio recorder. The speech-to-text functionality converts your spoken words into text for the chatbot to process.<br>
●	API Model Selection: Choose from available AI models to customize the chatbot’s response style and capabilities.<br>
●	Session Management: The chatbot maintains conversation context, allowing for coherent multi-turn dialogues.<br>

## Tips for Best Experience
●	Use clear and concise language when chatting.<br>
●	For document uploads, ensure files are not corrupted and are in supported formats.<br>
●	Speak clearly when using the audio recorder to improve speech recognition accuracy.<br>
●	Keep your OpenRouter API key secure and do not share it publicly.<br>

## Features
The AI Fun Chatbot boasts a rich set of features that combine to deliver a powerful and flexible AI interaction platform:<br>
●	Multi-Modal Input Support: Accepts text, document uploads (PDF and DOCX), and audio recordings.<br>
●	Document Text Extraction: Extracts text from PDFs and DOCX files using native parsing and OCR for scanned documents.<br>
●	Retrieval-Augmented Responses: Automatically indexes uploaded files with FAISS + sentence-transformers and injects top-k snippets into every LLM call.<br>
●	Speech-to-Text Conversion: Converts recorded audio into text using Google’s speech recognition API.<br>
●	Asynchronous API Calls: Utilizes asynchronous HTTP requests to OpenRouter’s API for efficient and responsive AI interactions.<br>
●	Customizable AI Models: Supports multiple AI models selectable by the user to tailor chatbot responses.<br>
●	Modern UI Design: Features a clean, responsive interface styled with Google Fonts and custom CSS for enhanced user experience.<br>
●	Session Persistence: Maintains chat history and context for ongoing conversations.<br>
●	Error Handling: Provides informative error messages for API failures or unsupported file types.<br>
●	Open Source and Extensible: Built with popular Python libraries, making it easy to extend and customize.<br>

## Required Dependencies
All Python dependencies live in `requirements.txt`, but the most important ones are listed below so you can validate Streamlit Cloud installs everything you need:<br>
●	streamlit: Main UI framework.<br>
●	aiohttp: Async HTTP client used by the OpenRouter wrapper.<br>
●	python-docx & PyPDF2: Native PDF/DOCX extraction.<br>
●	pdf2image, pytesseract, Pillow: Optional OCR pipeline for scanned PDFs.<br>
●	speech_recognition & audio_recorder_streamlit: Browser audio capture + Google STT integration.<br>
●	sentence-transformers, faiss-cpu, numpy, tiktoken: Retrieval-augmented generation stack (chunk embeddings, FAISS index, token-aware chunking).<br>
●	pydub & openai: Audio utilities and optional future LLM integrations.<br>
Make sure these install without errors before deploying publicly.<br>

## Running the Application
After completing the installation and setup, running the AI Fun Chatbot is straightforward:<br>
*	Activate your virtual environment (if not already active):<br>
source venv/bin/activate  # Windows: venv\Scripts\activate<br>
*	Start the Streamlit app:<br>
streamlit run fun_project_chatbot.py<br>
*	Access the chatbot interface:<br>
*	Open your web browser and navigate to the URL provided by Streamlit, typically http://localhost:8501.<br>
*  Begin interacting:<br>
* Use the chat input, upload documents, or record audio to start conversations with the AI.<br>
*	Stopping the app:<br>
*	Press Ctrl+C in the terminal to stop the Streamlit server.<br>

This comprehensive guide ensures you have all the information needed to install, run, and utilize the AI Fun Chatbot effectively. The project combines state-of-the-art AI interaction with practical document and speech processing, making it a valuable tool for a wide range of applications in research, education, and development. Enjoy exploring the capabilities of this versatile AI assistant! (OpenRouter Documentation) (Streamlit Documentation) (PyPDF2 Documentation) (pytesseract GitHub) (SpeechRecognition Documentation)<br>

## References:<br>
- OpenRouter Documentation. https://openrouter.ai/docs. <br>
- Streamlit Documentation. https://docs.streamlit.io. <br>
- PyPDF2 Documentation. https://pypdf2.readthedocs.io. <br>
- pytesseract GitHub. https://github.com/madmaze/pytesseract. <br>
- SpeechRecognition Documentation. https://pypi.org/project/SpeechRecognition/. <br>

# Support me:<br>
email    : abigivan99@gmail.com<br>
LinkedIn : [My_Profile](https://www.linkedin.com/in/abizar-al-gifari/)
