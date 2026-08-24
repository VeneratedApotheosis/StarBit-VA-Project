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
        Language.ZH: "zh_CN-huayan-medium",
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
    WHISPER_MODEL = Model.MEDIUM
    WHISPER_COMPUTE_TYPE = "default"  # default / int8 / float16

    # VAD Settings
    VAD_CONFIDENCE = 0.7
    VAD_STOP_SECS = 0.6
    VAD_START_SECS = 0.2
    MIN_VOLUME = 0.4

    # LLM Settings
    LLM_MODEL = "qwen3.5-uncensored:latest"

    # TTS Settings
    TTS_MODEL_PATH = Path("./models/piper")

    # Static Pipeline Constants
    AUDIO_SAMPLE_RATE = 16000