from config import Config

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.ollama.llm import OLLamaLLMService
from pipecat.services.whisper.stt import WhisperSTTService
from pipecat.services.piper.tts import PiperTTSService, PiperTTSSettings

from tools import get_tools
import tools

def create_stt_service() -> WhisperSTTService:
    # config whisper using settings
    stt = WhisperSTTService(
        settings=WhisperSTTService.Settings(
            # options: TINY, BASE, SMALL, MEDIUM, LARGE_V3_TURBO
            # instaalled: base, medium
            model=Config.WHISPER_MODEL,
            # select lang
            language=Config.get_whisper_language(),
            # probability threshold to filter out silence/background noise
            no_speech_prob=0.4,
        ),
        # hardware configuration
        device=Config.WHISPER_DEVICE,  # cuda / cpu | requires cublas installation for cuda
        compute_type=Config.WHISPER_COMPUTE_TYPE,
    )
    return stt


def create_vad_analyzer() -> SileroVADAnalyzer:
    # config silero vad
    vad_analyzer = SileroVADAnalyzer(
        sample_rate=Config.AUDIO_SAMPLE_RATE,
        params=VADParams(
            # lower if bot ignores quiet speakers.
            # raise if background noise triggers the bot
            confidence=Config.VAD_CONFIDENCE,
            # how much continuous speech is needed to trigger a turn
            start_secs=Config.VAD_START_SECS,
            # how much silence required to consider a turn complete
            stop_secs=Config.VAD_STOP_SECS,
            # minimum vol to be triggered
            min_volume=Config.MIN_VOLUME,
        ),
    )

    return vad_analyzer

def create_llm_context():
    # create LLM context
    context = LLMContext(
        # inject tools
        tools=tools.get_tools()
    )
    # inject system prompt
    context.add_message({
        "role": "system",
        "content": "You are a helpful AI Voice assistant. Answer concisely. By default, try to answer in Engllish."
    })

    return context

def create_llm_aggregators(context : LLMContext, vad_analyzer : SileroVADAnalyzer):
    aggregators = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=vad_analyzer),
    )
    return aggregators

def create_llm_service():
    # configure llm service
    llm = OLLamaLLMService(
        settings=OLLamaLLMService.Settings(
            model=Config.LLM_MODEL,
        )
    )
    return llm

def create_tts_service():
    # declare TTS service
    tts = PiperTTSService(
        download_dir = Config.TTS_MODEL_PATH,
        use_cuda=True,
        settings=PiperTTSSettings(
            voice=Config.get_piper_voice(),
        )
    )
    return tts