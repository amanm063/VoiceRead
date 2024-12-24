# 📖 VoiceRead

**VoiceRead** is an intuitive Streamlit-based application that converts text from PDF files into speech. With this app, users can upload a file, extract its textual content, and listen to it at a customizable speed.

**This app is made with the help of Claude, Perplexity, and ChatGPT.**

## Features
- **Upload and Process Files**: Supports PDF format for extracting text.
- **Text-to-Speech Conversion**: Utilizes `gTTS` (Google Text-to-Speech) to generate audio from the extracted text.
- **Playback Controls**: Users can adjust the reading speed with a slider for a personalized listening experience.
- **Interactive Text Preview**: Displays the extracted text in a scrollable and well-styled preview box.
- **Cross-Platform Compatibility**: Runs seamlessly on the Streamlit Community Cloud or any local machine with Python installed.

## How It Works
### File Upload
- Users can upload a PDF file using the file uploader widget.
- The app temporarily saves the file locally using Python's `tempfile` module.

### Text Extraction
1. **PDF Files**: 
   - Uses `PyPDF2` to extract text page by page. 
   - Start and end page options are provided for partial text extraction.

### Text-to-Speech
- After extracting the text, it is split into sentences.
- Each sentence is converted into audio using the `gTTS` library.
- Audio is played back using `pygame.mixer`.

### Threading for Smooth Operation
- A separate thread processes the audio playback to avoid blocking the main Streamlit app interface.
- `Queue` is used to manage sentences awaiting conversion.

### Styling and User Interface
- Modern UI enhancements using custom CSS:
  - Gradient background
  - Themed dark and light modes
  - Improved widgets and layout
- Interactive elements like sliders and buttons allow for an engaging experience.

## Getting Started
### Prerequisites
- Python 3.8 or higher
- Required Python libraries (see `requirements.txt`)

### Installation
1. Clone this repository:
2. Install the required libraries:
3. Run the application:

## Usage Instructions
1. Open the app in your web browser.
2. Upload a PDF file using the provided uploader.
3. Select your desired reading speed using the slider.
4. Click on "▶️ Start Reading" to begin listening to the extracted text.

## Contributing
Contributions are welcome! If you would like to contribute to this project, please fork the repository and submit a pull request.
