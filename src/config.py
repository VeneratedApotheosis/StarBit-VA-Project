from dotenv import load_dotenv
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pipecat.services.whisper.stt import Model
from pipecat.transcriptions.language import Language
load_dotenv()

class AppSettings(BaseSettings):
    # --------------------------------- Wake Word -------------------------------- #
    wake_phrases: list[str] = ["kina","kino","tina", "tino", "tiana", "tiano", "dino", "dina"]
    # ---------------------------------- Whisper --------------------------------- #
    whisper_device: str = "cuda"
    whisper_model: Model = Model.LARGE
    whisper_compute_type: str = "default"
    whisper_no_speech_prob: float = 0.4

    # ------------------------------------ VAD ----------------------------------- #
    vad_confidence: float = 0.5
    vad_stop_secs: float = 0.5
    vad_start_secs: float = 0.1
    vad_min_volume: float = 0.6

    # ------------------------------------ LLM ----------------------------------- #
    llm_model: str = "qwen3.5-uncensored:latest"

    # ------------------------------------ TTS ----------------------------------- #
    # Filter #
    md_filter_code: bool = True
    md_filter_tables: bool = True
    md_filter_repeated_sequences: bool = True
    
    # Kokoro #
    kokoro_model_file_name: str = "kokoro-v1.0"
    kokoro_voice_file_name: str = "voices-v1.0"
    kokoro_model_path: Path = Path(f"./models/kokoro/{kokoro_model_file_name}.onnx")
    kokoro_voice_path: Path = Path(f"./models/kokoro/{kokoro_voice_file_name}.bin")
    
    # Piper #
    piper_model_path: Path = Path("./models/piper") # zh_CN-xiao_ya-medium / en_US-libritts-high
    piper_use_cuda: bool = True
    piper_voice: str = "en_US-libritts-high"

    # ------------------------------ Pipeline Const ------------------------------ #
    audio_sample_rate: int = 16000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # ---------------------------------- Google ---------------------------------- #
    google_routes_api_key: str = os.getenv('GOOGLE_ROUTES_API_KEY')

# ---------------------------------------------------------------------------- #
#                          Specialized Configurations                          #
# ---------------------------------------------------------------------------- #
class EngConfig(AppSettings):
    whisper_language: Language = Language.EN
    piper_voice: str = "en_US-libritts_r-medium"
    system_prompt: str = (
    """
    # Identity and Role:
    You are Tina, an intelligent, helpful, and proactive voice AI assistant. Answer all responses in English unless specified by user otherwise. Your primary function is to answer user prompts.
    
    # Formatting and Output rules:
    Your output will be converted directly into audio via a Text-to-Speech engine. You MUST adhere to these speech formatting rules:
    1. Write exclusively in plain, conversational prose. Your response must contain only standard letters, numbers, spaces, periods, commas, and question marks.
    2. Aim to output one sentence responses. Do not output responses longer than 3 sentences.
    
    # Agentic Tool Usage Logic
    You have access to internal tools to retrieve information and take actions on behalf of the user.
    1. Autonomous Decision-Making: Call tools automatically whenever you lack sufficient context. 
    """
        )
    
class ChineseConfig(AppSettings):
    whisper_language: Language = Language.ZH
    piper_voice: str = "zh_CN-xiao_ya-medium"
    system_prompt: str = (
    """
    # 身份與角色：
    你是 Tina，一個智慧、有幫助且主動的語音 AI 助理。你的主要功能是回答使用者的提問。

    # 格式與輸出規則：
    你的輸出將透過文字轉語音（TTS）引擎直接轉為音訊。你必須遵守以下語音格式規則：
    1. 僅使用平實的口語表達。回應內容只能包含標準文字、數字、空格、句號、逗號及問號。
    2. 盡量以單句回答。回應長度嚴禁超過三句話。

    #工具使用邏輯：
    你可以使用內部工具來檢索資訊並代表使用者執行操作。
    1. 自主決策：每當缺乏足夠的上下文時，自動呼叫工具。
    """
        )
    
config = ChineseConfig()

# @property
# def whisper_language(self) -> Language:
#     mapping = {Language.EN: Language.EN, Language.ZH: Language.ZH}
#     return mapping.get(self.language, Language.EN)

# @property
# def piper_voice(self) -> str:
#     mapping = {
#         Language.EN: "en_US-lessac-medium",
#         Language.ZH: "zh_CN-xiao-ya-medium",
#     }
#     return mapping.get(self.language, "en_US-lessac-medium")
