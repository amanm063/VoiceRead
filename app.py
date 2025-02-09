import streamlit as st
import PyPDF2
import tempfile
import os
from gtts import gTTS
import base64
import io
import time

# Set up the app configuration
st.set_page_config(
    page_title="VoiceRead E-book",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for e-book styling
st.markdown("""
<style>
    /* Global styles */
    body {
        font-family: 'Georgia', serif;
        background-color: #f5f5f5;
        color: #2D3748;
    }
    
    /* Title styling */
    .app-title {
        font-size: 2rem;
        font-weight: 600;
        text-align: center;
        color: #2D3748;
        margin: 1rem 0;
        font-family: 'Georgia', serif;
    }
    
    /* E-book container */
    .ebook-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #fff;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Reading area */
    .reading-area {
        padding: 2rem;
        background-color: #fffff8;
        border-radius: 4px;
        border: 1px solid #e2e8f0;
        font-family: 'Georgia', serif;
        font-size: 18px;
        line-height: 1.8;
        margin: 1rem 0;
        min-height: 600px;
        overflow-y: auto;
    }
    
    /* Controls area */
    .controls-area {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Navigation buttons */
    .nav-buttons {
        display: flex;
        justify-content: space-between;
        margin: 1rem 0;
    }
    
    /* Custom file uploader */
    .uploadedFile {
        border: 2px dashed #cbd5e0;
        border-radius: 4px;
        padding: 2rem;
        text-align: center;
        background-color: #f8fafc;
    }
    
    /* Page numbers */
    .page-number {
        text-align: center;
        font-style: italic;
        color: #718096;
        margin-top: 1rem;
    }
    
    /* Reading progress */
    .progress-bar {
        height: 4px;
        background-color: #e2e8f0;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background-color: #4299e1;
        transition: width 0.3s ease;
    }
    
    /* Audio player */
    audio {
        width: 100%;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def calculate_read_time(text, speed):
    """Calculate reading time for text based on words and speed."""
    words = len(text.split())
    base_time = words * 0.6
    return max(base_time / speed, 1.0)

def extract_text_from_pdf(pdf_path, start_page=1, end_page=None):
    """Extract text from PDF with page range."""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        end_page = min(end_page or len(pdf_reader.pages), len(pdf_reader.pages))
        return '\n'.join(
            pdf_reader.pages[i].extract_text()
            for i in range(start_page - 1, end_page)
        )

def generate_audio_with_gtts(text, retries=3, backoff=2):
    """Generate audio with retry logic."""
    for attempt in range(retries):
        try:
            tts = gTTS(text=text, lang='en')
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            return mp3_fp.getvalue()
        except Exception as e:
            if attempt < retries - 1:
                st.warning(f"Retrying audio generation... ({attempt + 1}/{retries})")
                time.sleep(backoff * (2 ** attempt))
            else:
                st.error(f"Failed to generate audio: {str(e)}")
                return None

# App title and description
st.markdown('<h1 class="app-title">📚 VoiceRead E-book</h1>', unsafe_allow_html=True)

# Initialize session state for reading position
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# Sidebar controls
with st.sidebar:
    st.markdown("### Reader Settings")
    font_size = st.slider("Font Size", 14, 24, 18, 1)
    reading_speed = st.slider("Reading Speed", 0.5, 2.0, 1.0, 0.1)

# Main content area
with st.container():
    uploaded_file = st.file_uploader("Upload your book (PDF)", type=['pdf'])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        try:
            # Get total pages
            with open(tmp_file_path, 'rb') as file:
                total_pages = len(PyPDF2.PdfReader(file).pages)

            # Navigation controls
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                if st.button("← Previous"):
                    st.session_state.current_page = max(1, st.session_state.current_page - 1)
            with col2:
                st.markdown(f'<p class="page-number">Page {st.session_state.current_page} of {total_pages}</p>', 
                          unsafe_allow_html=True)
            with col3:
                if st.button("Next →"):
                    st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)

            # Extract and display text
            text = extract_text_from_pdf(tmp_file_path, st.session_state.current_page, 
                                       st.session_state.current_page)

            # Reading area with custom styling
            st.markdown(f'''
                <div class="reading-area" style="font-size: {font_size}px;">
                    {text}
                </div>
            ''', unsafe_allow_html=True)

            # Progress bar
            progress = (st.session_state.current_page / total_pages) * 100
            st.markdown(f'''
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress}%;"></div>
                </div>
            ''', unsafe_allow_html=True)

            # Audio controls
            if st.button("🔊 Read Aloud"):
                with st.spinner("Generating audio..."):
                    audio_data = generate_audio_with_gtts(text)
                    if audio_data:
                        b64 = base64.b64encode(audio_data).decode()
                        st.markdown(f'''
                            <audio controls autoplay>
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                        ''', unsafe_allow_html=True)

        finally:
            # Clean up
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    else:
        st.markdown('''
            <div class="uploadedFile">
                <h3>📚 Welcome to VoiceRead E-book</h3>
                <p>Upload a PDF to start reading with voice narration</p>
            </div>
        ''', unsafe_allow_html=True)