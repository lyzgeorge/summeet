import streamlit as st
import tempfile
import subprocess
import yaml
import datetime
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.models.groq import GroqTools

def convert_to_mp3(file):
    """Convert audio/video to MP3 using ffmpeg."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.input') as temp_in:
            temp_in.write(file.read())
            input_path = temp_in.name

        output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name

        subprocess.run(
            ['ffmpeg', '-y', '-i', input_path, '-ac', '1', '-ar', '22050', '-b:a', '96k', output_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg conversion failed: {e}")

# Load prompt templates
with open("summeet_prompts.yaml", "r") as f:
    prompts = yaml.safe_load(f)

transcriber = GroqTools(exclude_tools=["generate_speech", "translate_audio"])

st.set_page_config("Summeet - AI Meeting Summarizer", ":memo:", layout="wide")

# Sidebar: Upload or record
with st.sidebar:
    st.header("Upload Recording")
    audio_file = None

    tabs = st.tabs(["Upload File", "Record Now"])

    with tabs[0]:
        uploaded = st.file_uploader("Supported formats: mp3, wav, ogg, flac, m4a, aac, wma, aiff, mp4")
        if uploaded:
            st.success("File uploaded successfully!")
            audio_file = convert_to_mp3(uploaded)
            st.success("Converted to MP3!")

    with tabs[1]:
        recorded = st.audio_input("Record your meeting")
        if recorded:
            audio_file = convert_to_mp3(recorded)
            st.success(f"Recording converted to MP3!")

    st.session_state.output_audio_path = audio_file or st.session_state.get("output_audio_path")
    st.session_state.setdefault("transcription_result", "")
    st.session_state.setdefault("transcription_error", "")

    st.header("Transcribe Recording")
    if st.button("Transcribe"):
        if st.session_state.output_audio_path:
            try:
                with st.spinner("Transcribing..."):
                    st.session_state.transcription_result = transcriber.transcribe_audio(
                        audio_source=st.session_state.output_audio_path
                    )
                    st.success("Transcription completed!")
            except Exception as e:
                st.session_state.transcription_error = f"Transcription failed: {e}"
                st.error(st.session_state.transcription_error)
        else:
            st.warning("Please upload or record audio first.")

# Main interface
st.header("Summeet - AI Meeting Summarizer")
st.caption("← Upload/record and transcribe, or paste transcription below ↓")

transcription_text = st.text_area(
    "Transcription",
    value=st.session_state.transcription_result,
    height=200,
    help="Edit the transcribed text here if needed."
)
meeting_info = st.text_input("Meeting Information (optional)", placeholder="Date, Participants, Agenda...")

language = st.segmented_control(
    "Select Summary Language", options=["en", "cn", "es", "fr", "de"], default="en"
)

agent = Agent(
    name="Groq Transcription Agent",
    model=Groq(id="llama-3.3-70b-versatile"),
    instructions=prompts[language],
    markdown=True,
    debug_mode=True,
)

if st.button("Summarize"):
    if not transcription_text.strip():
        st.warning("Please provide transcription text.")
    else:
        try:
            with st.spinner("Generating summary..."):
                summary = agent.run(transcription_text + "\n***\n**Additional Meeting Info**\n" + meeting_info)
                st.session_state.summary_result = summary
                st.success("Summary generated!")
        except Exception as e:
            st.error(f"Summary generation failed: {e}")

# Output summary
st.session_state.setdefault("summary_result", None)
st.divider()
if st.session_state.summary_result:
    st.markdown(st.session_state.summary_result.content)
    st.download_button(
        "Download Summary",
        data=st.session_state.summary_result.content,
        file_name=f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}_summary.md",
        mime="text/markdown"
    )
