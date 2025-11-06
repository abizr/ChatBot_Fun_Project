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
This chatbot leverages asynchronous API calls to OpenRouter’s AI models, enabling real-time, intelligent conversations. It supports direct text extraction from documents, optical character recognition (OCR) for scanned PDFs, and speech recognition for audio inputs, making it a versatile tool for users who want to interact with AI in multiple modalities. The application is built with a modern, user-friendly interface using Streamlit, enhanced with custom styling and Google Fonts for an appealing visual experience.<br>
The project is ideal for developers, researchers, and enthusiasts interested in AI-driven conversational agents, document analysis, and speech processing technologies. It serves as a comprehensive example of integrating various Python libraries and APIs to create a sophisticated, multi-functional chatbot application.<br>

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
●	Speech-to-Text Conversion: Converts recorded audio into text using Google’s speech recognition API.<br>
●	Asynchronous API Calls: Utilizes asynchronous HTTP requests to OpenRouter’s API for efficient and responsive AI interactions.<br>
●	Customizable AI Models: Supports multiple AI models selectable by the user to tailor chatbot responses.<br>
●	Modern UI Design: Features a clean, responsive interface styled with Google Fonts and custom CSS for enhanced user experience.<br>
●	Session Persistence: Maintains chat history and context for ongoing conversations.<br>
●	Error Handling: Provides informative error messages for API failures or unsupported file types.<br>
●	Open Source and Extensible: Built with popular Python libraries, making it easy to extend and customize.<br>

## Required Dependencies
The project relies on several Python libraries to implement its diverse functionalities. Below is a detailed list of required dependencies, which are also included in the requirements.txt file:<br>
●	asyncio: For asynchronous programming and managing concurrent API calls.<br>
●	aiohttp: To perform asynchronous HTTP requests to the OpenRouter API.<br>
●	streamlit: The web framework used to build the interactive UI.<br>
●	io: For handling in-memory byte streams, especially for file processing.<br>
●	python-docx: To parse and extract text from DOCX files.<br>
●	PyPDF2: For reading and extracting text from PDF documents.<br>
●	pdf2image: Converts PDF pages into images for OCR processing.<br>
●	pytesseract: Python wrapper for Tesseract OCR engine to extract text from images.<br>
●	speech_recognition: To convert audio recordings into text using speech recognition APIs.<br>
●	audio_recorder_streamlit: Streamlit component for recording audio directly in the browser.<br>
Ensure all these packages are installed to guarantee full functionality of the chatbot.<br>

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
