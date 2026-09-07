import os
from pathlib import Path

from dotenv import load_dotenv
from pipecat.services.whisper.stt import Model
from pipecat.transcriptions.language import Language
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class AppSettings(BaseSettings):
    wake_phrases: list[str] = ["kina","kino","tina", "tino", "tiana", "tiano", "dino", "dina"]
    
    whisper_device: str = "cuda"
    whisper_model: Model = Model.LARGE
    whisper_compute_type: str = "default"
    whisper_no_speech_prob: float = 0.4
    whisper_language: Language = Language.EN

    vad_confidence: float = 0.4
    vad_stop_secs: float = 0.2
    vad_start_secs: float = 0.2
    vad_min_volume: float = 0.6

    llm_model: str = "qwen3.5-9b"
    llm_api_key: str = os.getenv("LLM_API_KEY", "dummy")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")

    md_filter_code: bool = True
    md_filter_tables: bool = True
    md_filter_repeated_sequences: bool = True

    ZH_filter_enabled: bool = False
    
    kokoro_model_file_name: str = "kokoro-v1.0"
    kokoro_voice_file_name: str = "voices-v1.0"
    kokoro_model_path: Path = Path(f"./models/kokoro/{kokoro_model_file_name}.onnx")
    kokoro_voice_path: Path = Path(f"./models/kokoro/{kokoro_voice_file_name}.bin")
    kokoro_voice: str = "placeholder"
    kokoro_language: Language = Language.EN
    
    piper_model_path: Path = Path("./models/piper")
    piper_use_cuda: bool = True
    piper_voice: str = "placeholder"

    audio_in_sample_rate: int = 16000
    audio_out_sample_rate: int = 24000

    ws_host: str = os.getenv("WS_HOST", "0.0.0.0")
    ws_port: int = int(os.getenv("WS_PORT", "8765"))

    google_routes_api_key: str = os.getenv("GOOGLE_ROUTES_API_KEY", "dummy")
    
    mcp_url: str = os.getenv("MCP_URL", "https://twenty-understood-phenomenon-lodging.trycloudflare.com/mcp")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class ENconf(AppSettings):
    whisper_language: Language = Language.EN
    ZH_filter_enabled: bool = False
    piper_voice: str = "en_US-libritts-high"
    kokoro_voice: str = "af_heart"
    kokoro_language: Language = Language.EN
    system_prompt: str = """
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
    
class ZHconf(AppSettings):
    whisper_language: Language = Language.ZH
    ZH_filter_enabled: bool = False
    piper_voice: str = "zh_CN-xiao_ya-medium"
    kokoro_voice: str = "zm_yundao"
    kokoro_language: Language = Language.ZH
    system_prompt: str = """
    # 身份与角色：
    你是 Tina，一个智慧、有帮助且主动的语音 AI 助理。你的主要功能是回答使用者的提问。除非另有说明，所有内容均以简体中文输出。 

    # 格式与输出规则：
    你的输出将透过文字转语音（TTS）引擎直接转为音讯。你必须遵守以下语音格式规则：
    1. 仅使用平实的口语表达。回应内容只能包含标准文字、数字、空格、句号、逗号及问号。 
    2. 尽量以单句回答。回应长度严禁超过三句话。 

    #工具使用逻辑：
    你可以使用内部工具来检索资讯并代表使用者执行操作。 
    1. 自主决策：每当缺乏足够的上下文时，自动呼叫工具。
    """
    
config = ENconf()