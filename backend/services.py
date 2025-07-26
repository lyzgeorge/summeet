import os
import tempfile
import subprocess
import assemblyai as aai
from openai import OpenAI
from datetime import datetime
import json

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "openai_api_key")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "assemblyai_api_key")
TEXT_MODEL_NAME = os.getenv("TEXT_MODEL_NAME", "gemini/gemini-2.0-flash")

# Initialize clients
client = None

def initialize_openai_client():
    """Initialize OpenAI client with proper error handling"""
    global client
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "openai_api_key":
            raise ValueError("OPENAI_API_KEY is not set or is using default value")
        
        client = OpenAI(
            api_key=OPENAI_API_KEY, 
            base_url=OPENAI_BASE_URL,
            timeout=60.0  # 60 second timeout
        )
        
        # Test the client with a simple request
        try:
            test_response = client.chat.completions.create(
                model=TEXT_MODEL_NAME,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            print(f"✅ OpenAI client connection test successful")
            print(f"✅ Initialized OpenAI client with base URL: {OPENAI_BASE_URL}")
            print(f"✅ Using model: {TEXT_MODEL_NAME}")
        except Exception as test_error:
            print(f"⚠️ Client created but connection test failed: {test_error}")
            print(f"✅ Initialized OpenAI client with base URL: {OPENAI_BASE_URL}")
            print(f"✅ Using model: {TEXT_MODEL_NAME}")
            # Still return True as the client was created successfully
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {e}")
        print(f"OPENAI_API_KEY set: {'Yes' if OPENAI_API_KEY and OPENAI_API_KEY != 'openai_api_key' else 'No'}")
        print(f"OPENAI_BASE_URL: {OPENAI_BASE_URL}")
        client = None
        return False

# Initialize OpenAI client
initialize_openai_client()

# Initialize AssemblyAI
try:
    aai.settings.api_key = ASSEMBLYAI_API_KEY
    aai.settings.http_timeout = 900  # 15 minutes
    print(f"✅ Initialized AssemblyAI client")
    print(f"ASSEMBLYAI_API_KEY set: {'Yes' if ASSEMBLYAI_API_KEY and ASSEMBLYAI_API_KEY != 'assemblyai_api_key' else 'No'}")
except Exception as e:
    print(f"❌ Error initializing AssemblyAI: {e}")

# System prompts for meeting summarization
SYSTEM_PROMPTS = {
    "en": '''You will receive a meeting transcript without speaker attributions, with each sentence on a new line. Your task is to:

1. Match Speakers
   - Infer different speakers based on tone, content, and contextual logic.
   - Utilize any provided speaker information (including Speaker name, Description R&R, or intent) to aid in the judgment.
2. Calibrate Content
   - Identify and correct errors caused by speech-to-text transcription, such as typos, omissions, and redundant words.
   - Optimize the expression of proper nouns and terminology based on context to ensure accuracy.
3. Write Concise Meeting Minutes (Avoid vague statements and lengthy dialogues)
   - **Maintain a clear structure and focus on core information**, suitable for meeting records or sharing with non-attendees.
   - Extract key discussion points, decisions, and action items. Details should be specific, avoiding irrelevant conversations, repetitive content, and redundant descriptions.
   - Describe key content using keywords and phrases whenever possible, without necessarily using complete sentences.

------

**Meeting Minutes Output Format**
### **Meeting Background**
(Briefly state the meeting topic)
### **Main Agenda**
(List the core meeting topics using gerund phrases and a one-sentence summary)
### **Discussion Points**
- **Agenda Item 1:** (Specific arguments, key time points, or data, concise and to the point)
- **Agenda Item 2:** (Same as above)
- ……
- **Agenda Item n:** (Same as above)
### **Decisions and Action Items**
- **Decision:** (Clearly state the final decision or consensus, short and clear)
- **Action Items:** (List specific tasks, responsible parties, and deadlines)

------

Follow the above requirements step by step. Return only the meeting minutes in the main body, without presenting thought processes or dialogue.
''',

    "cn": '''你将到一份未经标注演讲者的会议转录文本，每句文本单独换行。你的任务是：

1. **匹配演讲者**
   - 根据语气、内容、上下文逻辑，推测不同发言者。
   - 利用可能提供的演讲者信息（包括 Speaker 姓名，Description R&R 或意图）辅助判断。
2. **校准内容**
   - 识别并修正因语音转写导致的错误，如错别字、漏字、冗余词。
   - 根据上下文，优化专有名词、术语表达，确保准确。
3. **撰写精炼的会议纪要**（**避免空洞表述及冗长对话**）
   - **结构清晰，直击核心信息**，适用于会议记录或分享给未参会者。
   - 提炼关键讨论点、决策、行动项，细节应具体，避免无关对话、重复内容和冗余描述。
   - 尽量使用关键词和短语的方式描述关键内容，不必使用完整的句式来表达。

----

**会议纪要输出格式**

### **会议背景**
（简要说明会议主题）
### **主要议题**
（列出会议核心议题，使用动名词短语和一句话总结）
### **讨论内容**
- **议题 1：**（具体论点、关键时间点或数据，简明扼要）
- **议题 2：**（同上）
- ……
- **议题 n：**（同上）
### **决策与行动项**
- **决策：**（明确最终决定或共识，简短而清晰）
- **行动项：**（列出具体执行任务、负责人及时间节点）

----

按照上述要求，逐步执行。在正文中仅返回会议纪要，不要呈现思考过程和回答等对话。
'''
}

def convert_to_mp3(input_file):
    """Convert input audio file to MP3 using ffmpeg directly."""
    try:
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        output_path = temp_output.name
        temp_output.close()

        command = [
            'ffmpeg', '-y',
            '-i', input_file,
            '-ac', '1',            # mono
            '-ar', '16000',        # 16kHz
            '-b:a', '64k',         # 64 kbps
            output_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {e}")

def clean_temp_files(file_list):
    """Clean up temporary files."""
    for file_path in file_list:
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Could not delete temp file {file_path}: {e}")
            pass

def transcribe_audio(audio_file, word_boost="", language="auto"):
    """
    Transcribe the audio file using AssemblyAI, waiting for completion.
    Returns dict with transcript text and speakers info.
    """
    if not audio_file:
        raise ValueError("No audio file provided")

    temp_files = []
    mp3_file = None
    try:
        mp3_file = convert_to_mp3(audio_file)
        temp_files.append(mp3_file)

        config_kwargs = {
            "speaker_labels": True,
            "language_detection": True if language == "auto" else False,
            "language_code": None if language == "auto" else language,
            "word_boost": [word.strip() for word in word_boost.split(",")] if word_boost else None,
        }

        # Clean None values
        config = aai.TranscriptionConfig(**{k: v for k, v in config_kwargs.items() if v is not None})
        transcriber = aai.Transcriber()

        # Use transcribe() which waits for the result
        transcript = transcriber.transcribe(mp3_file, config=config)
        print(f"Transcription id: {transcript.id}")

        # Process the result
        if transcript.status == aai.TranscriptStatus.completed:
            transcript_text = ""
            speaker_set = set()

            if transcript.utterances:
                for utterance in transcript.utterances:
                    speaker = utterance.speaker if utterance.speaker else "Unknown"
                    transcript_text += f"Speaker {speaker}: {utterance.text}\n"
                    speaker_set.add(speaker)
            else:
                transcript_text = transcript.text if transcript.text else "(No speech detected or transcription empty)"
                speaker_set.add("Unknown")

            # Ensure speaker_set has at least one entry if transcript_text exists
            if not speaker_set and transcript_text and transcript_text != "(No speech detected or transcription empty)":
                speaker_set.add("Unknown")

            # Sort speakers
            try:
                sorted_speakers = sorted(list(speaker_set), key=lambda x: (int(x) if x.isdigit() else float('inf'), x))
            except:
                sorted_speakers = sorted(list(speaker_set))

            # Create speakers JSON string for database storage
            speakers_data = [{"speaker": speaker, "description": ""} for speaker in sorted_speakers]
            
            return {
                "text": transcript_text,
                "speakers": json.dumps(speakers_data)
            }

        elif transcript.status == aai.TranscriptStatus.error:
            raise RuntimeError(f"Transcription Error: {transcript.error}")
        else:
            raise RuntimeError(f"Transcription ended with status: {transcript.status}")

    except Exception as e:
        raise RuntimeError(f"Error during transcription process: {str(e)}")
    finally:
        clean_temp_files(temp_files)

def summarize_meeting(transcript, speaker_table=None, system_prompt_language="en", temperature=0.8):
    """Summarize meeting transcript with optional speaker information."""
    if not transcript or transcript.strip() == "" or transcript.strip() == "(No speech detected or transcription empty)":
        return "No transcript available to summarize."

    if client is None:
        print("⚠️ OpenAI client is None, attempting to reinitialize...")
        if not initialize_openai_client():
            raise RuntimeError(
                f"OpenAI client is not initialized. Please check your configuration:\n"
                f"- OPENAI_API_KEY: {'Set' if OPENAI_API_KEY and OPENAI_API_KEY != 'openai_api_key' else 'NOT SET'}\n"
                f"- OPENAI_BASE_URL: {OPENAI_BASE_URL}\n"
                f"- TEXT_MODEL_NAME: {TEXT_MODEL_NAME}"
            )

    system_prompt = SYSTEM_PROMPTS.get(system_prompt_language, SYSTEM_PROMPTS["en"])

    try:
        speaker_info_str = ""
        if speaker_table:
            # speaker_table is expected to be a list of [speaker_name, description] pairs
            speaker_info_str = "\n\nSpeaker Information:\n" + "\n".join(
                [f"Speaker {row[0]}: {row[1]}" for row in speaker_table if len(row) > 1 and row[1].strip()]
            )
            
        content = f"Transcription:\n{transcript}\n----{speaker_info_str}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]

        print(f"Making OpenAI request with model: {TEXT_MODEL_NAME}")
        print(f"Messages: {len(messages)} messages")
        print(f"Temperature: {temperature}")
        
        response = client.chat.completions.create(
            model=TEXT_MODEL_NAME,
            messages=messages,
            temperature=temperature
        )
        
        print(f"OpenAI response received successfully")
        summary = response.choices[0].message.content.strip()
        
        if not summary:
            return "(Summary generation failed or produced empty result)"
        return summary

    except Exception as e:
        raise RuntimeError(f"Summarization error: {str(e)}")

def save_summary_as_markdown(transcript, summary, filename_base=None):
    """Save summary and transcript as markdown file."""
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"meeting_{now_str}.md"

    save_dir = os.path.join(tempfile.gettempdir(), "meeting_summaries")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    content = f"## {filename_base or 'Meeting'} - {now_str}\n\n***\n\n### Summary\n\n{summary}\n\n"

    if transcript:
        content += f"\n\n***\n\n### Full Transcript\n\n{transcript}\n\n"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Summary saved to: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error saving markdown file: {e}")
        raise RuntimeError(f"Error saving markdown file: {e}")