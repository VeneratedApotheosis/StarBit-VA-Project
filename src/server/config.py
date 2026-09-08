import os
from pathlib import Path

from dotenv import load_dotenv
from pipecat.services.whisper.stt import Model
from pipecat.transcriptions.language import Language
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class AppSettings(BaseSettings):
    wake_phrases: list[str] = ["kina","kino","tina", "tino", "tiana", "tiano", "dino", "dina"]
    
    # gpu requires 'sudo apt install cuda'
    whisper_device: str = "cuda" # "cpu", "cuda", or "auto"
    
    whisper_model: Model = Model.LARGE
    whisper_compute_type: str = "default"
    whisper_no_speech_prob: float = 0.4
    whisper_language: Language = Language.EN

    vad_confidence: float = 0.4
    vad_stop_secs: float = 0.2
    vad_start_secs: float = 0.2
    vad_min_volume: float = 0.6

    llm_model: str = "Qwen3.5-9B-AWQ-4bit"
    llm_api_key: str = os.getenv("LLM_API_KEY", "dummy")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")

    md_filter_code: bool = True
    md_filter_tables: bool = True
    md_filter_repeated_sequences: bool = True

    ZH_filter_enabled: bool = True
    
    kokoro_model_file_name: str = "kokoro-v1.0"
    kokoro_voice_file_name: str = "voices-v1.0"
    kokoro_model_path: Path = Path(f"./models/kokoro/{kokoro_model_file_name}.onnx")
    kokoro_voice_path: Path = Path(f"./models/kokoro/{kokoro_voice_file_name}.bin")
    kokoro_voice: str = "placeholder"
    kokoro_language: Language = Language.EN
    
    piper_model_path: Path = Path("./models/piper")
    piper_use_cuda: bool = True
    piper_voice: str = "placeholder"
    
    xtts_base_url: str = "http://localhost:8001"
    xtts_reference_audio: Path = Path("placeholder")
    xtts_language: str ="placeholder" # 'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh-cn', 'hu', 'ko', 'ja', 'hi', 'auto'

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
    
    xtts_reference_audio: Path = Path("temp/en-sample.wav")
    xtts_language: str ="en"
    
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
    kokoro_voice: str = "zf_xiaoyi"
    kokoro_language: str = "zh"
    
    xtts_reference_audio: Path = Path("temp/zh-cn-sample.wav")
    xtts_language: str ="zh-cn"
    
    system_prompt: str = """
    # 身份与角色
    你是 Tina，一位高效、专业且主动的企业办公语音 AI 助理。你的主要功能是协助员工处理日常办公任务、日程安排、资讯检索及工作流程咨询。除非另有说明，所有回应必须使用简体中文。

    # 语音输入容错规则
    用户的输入内容由语音识别（STT）系统生成，可能包含同音错别字、声调偏差、断句错误或语法不通顺。你必须结合办公场景上下文自动推断使用者的真实意图，严禁纠正或提及 STT 的识别错误。

    # 语音合成（TTS）输出规则
    你的文字输出将直接送入 TTS 引擎转换为语音，必须严格遵守以下规则：
    1. **纯口语表达：** 仅使用自然流畅的口语。严禁使用 Markdown 格式、标点符号以外的特殊符号、列表、Emoji 或缩写。
    2. **字符限制：** 输出内容只能包含汉字、阿拉伯数字、空格、句号、逗号及问号。
    3. **数字与专有名词：** 涉及时间、日期或数量时，直接使用汉字或清晰数字表达（如“十一点半”或“11点30分”），避免使用易产生歧义的符号（如以“11:30”代替“11点30分”）。
    4. **长度限制：** 回应控制在 1 到 3 句话以内，优先使用单句。

    # 工具调用逻辑
    你可以调用内部工具检索企业数据或执行办公操作。
    1. **自主决策：** 当缺乏必要的业务数据或上下文时，自动调用工具获取信息。
    2. **参数缺失：** 若执行具体操作所需的关键参数缺失且无法从上下文推断，仅允许提出一个具体的澄清问题。
    """
    
config = ZHconf()