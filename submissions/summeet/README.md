# Summeet - AI Meeting Summarizer

Summeet is a Streamlit-based application that leverages AI to transcribe audio recordings and generate concise meeting summaries. It supports various audio/video formats for upload and also allows direct audio recording within the application. The summaries can be generated in multiple languages and downloaded as Markdown files.

## Features

*   **Audio Transcription:** Transcribe meeting audio from uploaded files (MP3, WAV, OGG, FLAC, M4A, AAC, WMA, AIFF, MP4) or directly recorded audio.
*   **MP3 Conversion:** Automatically converts uploaded/recorded audio to MP3 format using `ffmpeg` for consistent processing.
*   **AI-Powered Summarization:** Utilizes the `Groq` model (specifically `llama-3.3-70b-versatile`) via the `agno` library to generate intelligent meeting summaries.
*   **Multi-language Support:** Generate summaries in English (en), Chinese (cn), Spanish (es), French (fr), and German (de).
*   **Customizable Meeting Info:** Option to include additional meeting information (date, participants, agenda) to enhance summary context.
*   **Downloadable Summaries:** Download generated summaries as Markdown files.
*   **User-Friendly Interface:** Built with Streamlit for an intuitive web interface.

## Installation

To set up and run Summeet locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/lyzgeorge/summeet.git
    cd summeet/submissions/summeet
    ```

2.  **Install `ffmpeg`:**
    Summeet uses `ffmpeg` for audio conversion. Ensure it is installed on your system.

    *   **macOS (using Homebrew):**
        ```bash
        brew install ffmpeg
        ```
    *   **Ubuntu/Debian:**
        ```bash
        sudo apt update
        sudo apt install ffmpeg
        ```
    *   **Windows:**
        Download the `ffmpeg` binaries from [ffmpeg.org](https://ffmpeg.org/download.html) and add them to your system's PATH.

3.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up Groq API Key:**
    The application requires a Groq API key for transcription and summarization. Set it as an environment variable:
    ```bash
    export GROQ_API_KEY="your_groq_api_key_here"
    ```
    Replace `"your_groq_api_key_here"` with your actual Groq API key.

## Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

2.  **Access the application:**
    Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3.  **Transcribe and Summarize:**
    *   **Upload File:** Use the "Upload File" tab in the sidebar to upload an audio/video recording.
    *   **Record Now:** Use the "Record Now" tab to record audio directly.
    *   Click the "Transcribe" button to get the transcription.
    *   Review and edit the transcription in the text area.
    *   Optionally, add "Meeting Information" for better context.
    *   Select the desired summary language.
    *   Click the "Summarize" button to generate the meeting summary.
    *   Download the summary using the "Download Summary" button.

## Technologies Used

*   **Python**
*   **Streamlit:** For building the web application interface.
*   **Agno:** Agent framework for AI model interaction.
*   **Groq:** AI model provider for transcription and summarization.
*   **PyYAML:** For loading prompt templates.
*   **FFmpeg:** For audio/video conversion.