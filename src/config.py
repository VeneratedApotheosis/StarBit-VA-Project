import os
from pathlib import Path
from dotenv import load_dotenv
from pipecat.services.whisper.stt import Model
from pipecat.transcriptions.language import Language

load_dotenv(override=True)

class Config:
    # Universal Language Setting
    LANGUAGE = Language.EN  # Options: Language.EN, Language.ZH, etc.

    # Language Mapping Configuration
    WHISPER_LANGUAGE_MAP = {
        Language.EN: Language.EN,
        Language.ZH: Language.ZH,
    }

    PIPER_VOICE_MAP = {
        Language.EN: "en_US-lessac-medium",
        Language.ZH: "zh_CN-xiao-ya-medium",
    }

    # Helper Methods for Service Consumption
    @classmethod
    def get_whisper_language(cls) -> Language:
        return cls.WHISPER_LANGUAGE_MAP.get(cls.LANGUAGE, Language.EN)

    @classmethod
    def get_piper_voice(cls) -> str:
        return cls.PIPER_VOICE_MAP.get(cls.LANGUAGE, "en_US-lessac-medium")

    # Whisper Settings
    WHISPER_DEVICE = "cuda"
    WHISPER_MODEL = Model.LARGE_V3_TURBO
    WHISPER_COMPUTE_TYPE = "default"  # default / int8 / float16

    # VAD Settings
    VAD_CONFIDENCE = 0.7
    VAD_STOP_SECS = 0.6
    VAD_START_SECS = 0.2
    MIN_VOLUME = 0.4

    # LLM Settings
    LLM_MODEL = "qwen3.5-uncensored:latest"
    SYSTEM_PROMPT = """
    You are a friendly, conversational AI voice assistant equipped with various real-time tools (including weather forecasts, location geocoding, and time).

    CORE VOICE & LANGUAGE RULES:
    1. LANGUAGE: Respond exclusively in natural, spoken English. Accept both Chinese and English input from the user, but ALWAYS answer in English.
    2. STRICT LENGTH: Keep every response under 2 to 3 spoken sentences (maximum 40 Chinese characters). Be direct and concise.
    3. TTS FORMATTING: Output strictly plain text. NEVER use markdown, bolding, asterisks, hash tags, bullet points, or special characters that confuse text-to-speech engines.
    4. SPOKEN NUMBERS & UNITS: Express dates, numbers, and weather units in natural spoken English.
    5. TOOL USAGE & DATA DUMPS: Silently call tools when real-time information (weather, location, time) is needed. Never mention function names or parameters. Summarize tool data into a single casual sentence—NEVER read full data lists or daily arrays.
    6. CONVERSATIONAL FLOW: Speak naturally as if on a phone call. End responses cleanly to hand the turn back to the user.
    """
    

    # TTS Settings
    TTS_MODEL_PATH = Path("./models/piper")

    # Static Pipeline Constants
    AUDIO_SAMPLE_RATE = 16000