from config import config
import tools as tools

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams

from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.turns.user_turn_strategies import UserTurnStrategies
from pipecat.turns.user_start import VADUserTurnStartStrategy
from pipecat.turns.user_start import WakePhraseUserTurnStartStrategy
from pipecat.turns.user_start import (
    KrispVivaIPUserTurnStartStrategy,
    TranscriptionUserTurnStartStrategy,
)
from pipecat.turns.user_stop import SpeechTimeoutUserTurnStopStrategy

from pipecat.services.ollama.llm import OLLamaLLMService
from pipecat.services.whisper.stt import WhisperSTTService
from pipecat.utils.text.markdown_text_filter import MarkdownTextFilter
from pipecat.services.piper.tts import PiperTTSService, PiperTTSSettings
from pipecat.services.kokoro.tts import KokoroTTSService

from pipecat.transports.local.audio import (
    LocalAudioTransport,
    LocalAudioTransportParams,
)

def create_stt_service() -> WhisperSTTService:
    stt = WhisperSTTService(
        settings=WhisperSTTService.Settings(
            model=config.whisper_model,
            language=config.whisper_language,
            no_speech_prob=config.whisper_no_speech_prob,
        ),
        device=config.whisper_device,
        compute_type=config.whisper_compute_type,
    )
    return stt


def create_vad_analyzer() -> SileroVADAnalyzer:
    vad_analyzer = SileroVADAnalyzer(
        sample_rate=config.audio_sample_rate,
        params=VADParams(
            confidence=config.vad_confidence,
            start_secs=config.vad_start_secs,
            stop_secs=config.vad_stop_secs,
            min_volume=config.vad_min_volume,
        ),
    )
    return vad_analyzer


def create_llm_context():
    context = LLMContext(
        tools=tools.get_tools()
    )
    context.add_message({
        "role": "system",
        "content": config.system_prompt
    })
    return context


def create_llm_aggregators(context: LLMContext, vad_analyzer: SileroVADAnalyzer):
    wake_start_strategy = WakePhraseUserTurnStartStrategy(
        phrases=config.wake_phrases,
    )
    speech_timeout_strategy = SpeechTimeoutUserTurnStopStrategy(user_speech_timeout=0.6)

    
    aggregators = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=vad_analyzer,
            user_turn_strategies=UserTurnStrategies(
                start=[wake_start_strategy],
                stop=[speech_timeout_strategy],
            ),
        ),
    )
    return aggregators


def create_llm_service():
    llm = OLLamaLLMService(
        settings=OLLamaLLMService.Settings(
            model=config.llm_model,
        )
    )
    return llm


def create_tts_service():
    md_filter = MarkdownTextFilter(
        params=MarkdownTextFilter.InputParams(
            filter_code=config.md_filter_code,
            filter_tables=config.md_filter_tables,
            filter_repeated_sequences=config.md_filter_repeated_sequences
        )
    )
    # # piper
    # tts = PiperTTSService(
    #     download_dir=config.piper_model_path,
    #     use_cuda=config.piper_use_cuda,
    #     text_filters=[md_filter],
    #     settings=PiperTTSSettings(
    #         voice=config.piper_voice,
    #     )
    # )
    
    # kokoro
    tts = KokoroTTSService(
        model_path=config.kokoro_model_path,
        voices_path=config.kokoro_voice_path,
        settings=KokoroTTSService.Settings(
            voice="af_heart",
        ),
    )
    
    return tts

def create_transport():
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_in_sample_rate=config.audio_sample_rate,  # silero expects 8kHz or 16000Hz (16k recommended)
            audio_out_enabled=True,
            audio_out_sample_rate=config.audio_sample_rate,
        )
    )
    return transport