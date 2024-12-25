import streamlit as st
import PyPDF2
import tempfile
import os
from gtts import gTTS
from pygame import mixer
import threading
from queue import Queue
import io

# Initialize the mixer for audio playback
mixer.init()

def extract_text_from_pdf(pdf_path, start_page=1, end_page=None):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        end_page = min(end_page or len(pdf_reader.pages), len(pdf_reader.pages))
        return '\n'.join(
            pdf_reader.pages[i].extract_text()
            for i in range(start_page - 1, end_page)
        )

def text_to_speech_worker(sentence_queue, speed):
    """Worker function for converting text to speech."""
    while True:
        sentence = sentence_queue.get()
        if sentence is None:
            break
        
        tts = gTTS(text=sentence, lang='en', slow=(speed < 1))
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        sound = mixer.Sound(mp3_fp)
        sound.play()
        while mixer.get_busy():
            continue
        
        sentence_queue.task_done()

# Streamlit app configuration
st.set_page_config(
    page_title="VoiceRead",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS for styling the app
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #f6f8fa, #eef2f3);
}
.main > div {
    padding-top: 1rem;
}
.app-title {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    color: #3A3B3C;
    margin-bottom: 1.5rem;
}
.stButton > button {
    background-color: #4CAF50 !important;
    color: white !important;
    border-radius: 5px !important;
    padding: 0.5rem 1rem !important;
    font-size: 1rem !important;
    font-weight: bold !important;
}
.stButton > button:hover {
    background-color: #45a049 !important;
}
.preview-box {
    padding: 1.5rem;
    border-radius: 0.5rem;
    background-color: #ffffff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    height: 400px;
    overflow-y: auto;
    font-size: 1rem;
    line-height: 1.6;
}
.upload-message {
    text-align: center;
    padding: 2rem;
    border: 2px dashed #ddd;
    border-radius: 0.5rem;
    background-color: #fafafa;
    margin: 2rem 0;
    font-size: 1.2rem;
    color: #666;
}
[data-testid="stFileUploadDropzone"] {
    background: #ffffff !important;
}
@media (prefers-color-scheme: dark) {
body {
    background: linear-gradient(135deg, #1e1e1e, #121212);
}
.app-title {
    color: #f0f0f0;
}
.preview-box {
    background-color: #1e1e1e;
    color: #f0f0f0;
    border: 1px solid #333;
}
.upload-message {
    border-color: #333;
    background-color: #1e1e1e;
    color: #ddd;
}
[data-testid="stFileUploadDropzone"] {
    background: #1e1e1e !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for audio queue and worker thread
if 'audio_queue' not in st.session_state:
    st.session_state.audio_queue = Queue()
if 'worker_thread' not in st.session_state:
    st.session_state.worker_thread = None

# App title
st.markdown('<h1 class="app-title">📖 VoiceRead</h1>', unsafe_allow_html=True)

# File uploader and reading speed slider
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
with col2:
    speed = st.slider("Reading Speed", 0.5, 2.0, 1.0, 0.1)

def start_reading(text, speed):
    """Start reading the extracted text."""
    if st.session_state.worker_thread and st.session_state.worker_thread.is_alive():
        st.session_state.audio_queue.put(None)
        st.session_state.worker_thread.join()

    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    st.session_state.audio_queue = Queue()
    
    st.session_state.worker_thread = threading.Thread(
        target=text_to_speech_worker,
        args=(st.session_state.audio_queue, speed)
    )
    
    st.session_state.worker_thread.start()

    for sentence in sentences:
        st.session_state.audio_queue.put(sentence)

if uploaded_file:
    
   with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
       tmp_file.write(uploaded_file.getvalue())
       tmp_file_path = tmp_file.name

   try:
       text = ""
       
       if uploaded_file.type == "application/pdf":
           total_pages = len(PyPDF2.PdfReader(tmp_file_path).pages)
           col1, col2 = st.columns(2)
           with col1:
               start_page = st.number_input("Start Page", min_value=1, value=1, step=1)
           with col2:
               end_page = st.number_input("End Page", min_value=start_page, max_value=total_pages, value=start_page, step=1)
           text = extract_text_from_pdf(tmp_file_path, start_page, end_page)

       if text:
           if st.button("▶️ Start Reading", key="start_reading"):
               with st.spinner("Generating audio..."):
                   start_reading(text, speed)
           st.markdown(f'<div class="preview-box">{text}</div>', unsafe_allow_html=True)

   finally:
       if os.path.exists(tmp_file_path):
           os.unlink(tmp_file_path)
else:
   st.markdown('<div class="upload-message">📖 Upload a PDF file to begin</div>', 
               unsafe_allow_html=True)
