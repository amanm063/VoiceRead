import streamlit as st
import PyPDF2
import tempfile
import os
import pyttsx3
import base64
import io

# Set up the app configuration
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
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_path, start_page=1, end_page=None):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        end_page = min(end_page or len(pdf_reader.pages), len(pdf_reader.pages))
        return '\n'.join(
            pdf_reader.pages[i].extract_text()
            for i in range(start_page - 1, end_page)
        )

def generate_audio_with_pyttsx3(text):
    """Generate audio using pyttsx3."""
    engine = pyttsx3.init()
    audio_fp = io.BytesIO()
    engine.save_to_file(text, 'temp_audio.mp3')
    engine.runAndWait()
    
    # Read the saved file into memory and clean up
    with open('temp_audio.mp3', 'rb') as file:
        audio_fp.write(file.read())
    os.remove('temp_audio.mp3')
    audio_fp.seek(0)
    return audio_fp.getvalue()

# Initialize session state
if 'reading' not in st.session_state:
    st.session_state.reading = False

# App title
st.markdown('<h1 class="app-title">📖 VoiceRead</h1>', unsafe_allow_html=True)

# File uploader and reading speed slider
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
with col2:
    speed = st.slider("Reading Speed", 0.5, 2.0, 1.0, 0.1)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # Get total pages
        with open(tmp_file_path, 'rb') as file:
            total_pages = len(PyPDF2.PdfReader(file).pages)

        # Page selection
        col1, col2 = st.columns(2)
        with col1:
            start_page = st.number_input("Start Page", min_value=1, value=1, step=1)
        with col2:
            end_page = st.number_input("End Page", min_value=start_page, 
                                     max_value=total_pages, value=start_page, step=1)

        # Extract text
        text = extract_text_from_pdf(tmp_file_path, start_page, end_page)

        # Generate and play audio when button is clicked
        if st.button("▶️ Start Reading"):
            with st.spinner("Generating audio..."):
                # Generate audio using pyttsx3
                audio_data = generate_audio_with_pyttsx3(text)
                
                if audio_data:
                    # Convert audio to base64 and display the player
                    b64 = base64.b64encode(audio_data).decode()
                    audio_html = f"""
                        <audio autoplay controls>
                            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                        </audio>
                    """
                    st.markdown(audio_html, unsafe_allow_html=True)

        # Display full text preview
        st.markdown("### Full Text Preview")
        st.markdown('<div class="preview-box">' + text + '</div>', unsafe_allow_html=True)

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

else:
    st.markdown('<div class="upload-message">📖 Upload a PDF file to begin</div>', unsafe_allow_html=True)
