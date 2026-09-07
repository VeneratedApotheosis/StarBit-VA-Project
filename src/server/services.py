import opencc
import tools
from config import config
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (
    AudioRawFrame,
    Frame,
    InputAudioRawFrame,
    OutputAudioRawFrame,
    TextFrame,
)
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.processors.filters.frame_filter import FrameFilter
from pipecat.serializers.protobuf import ProtobufFrameSerializer
from pipecat.services.kokoro.tts import KokoroTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.piper.tts import PiperTTSService
from pipecat.services.whisper.stt import WhisperSTTService
from pipecat.transports.websocket.server import (
    SingleClientWebsocketServerParams,
    SingleClientWebsocketServerTransport,
)
from pipecat.turns.user_start import (
    VADUserTurnStartStrategy,
    WakePhraseUserTurnStartStrategy,
)
from pipecat.turns.user_stop import (
    SpeechTimeoutUserTurnStopStrategy,
    TurnAnalyzerUserTurnStopStrategy,
)
from pipecat.turns.user_turn_strategies import UserTurnStrategies
from pipecat.utils.text.base_text_filter import BaseTextFilter
from pipecat.utils.text.markdown_text_filter import MarkdownTextFilter


# ---------------------------------- Helper ---------------------------------- #
class ChinesePunctuationFilter(BaseTextFilter):
    def __init__(self):
        self._replacements = {
            ",": "，",
            ".": "。",
            "?": "？",
            "!": "！",
            ":": "：",
            ";": "；",
        }
        self._converter = opencc.OpenCC('t2s')

    def filter(self, text: str) -> str:
        for eng, chi in self._replacements.items():
            text = text.replace(eng, chi)
        return self._converter.convert(text)

# --------------------------------- services --------------------------------- #
def create_stt_service() -> WhisperSTTService:
    stt = WhisperSTTService(
        settings=WhisperSTTService.Settings(
            model=config.whisper_model,
            # language=config.whisper_language,
            no_speech_prob=config.whisper_no_speech_prob,
        ),
        device=config.whisper_device,
        compute_type=config.whisper_compute_type,
    )
    return stt


def create_vad_analyzer() -> SileroVADAnalyzer:
    vad_analyzer = SileroVADAnalyzer(
        sample_rate=config.audio_in_sample_rate,
        params=VADParams(
            confidence=config.vad_confidence,
            start_secs=config.vad_start_secs,
            stop_secs=config.vad_stop_secs,
            min_volume=config.vad_min_volume,
        ),
    )
    return vad_analyzer

async def create_llm_aggregators(vad_analyzer: SileroVADAnalyzer) -> LLMContextAggregatorPair:
    # register all tools
    mcp_tools = (await tools.get_mcp_tools()).standard_tools # extracts list of tools
    # pipecat wraps list of tools around the ToolsSchema class, for the sake of these programs, it's better to work with lists of tools
    local_tools = tools.get_static_tools() 
    
    all_tools = mcp_tools + local_tools
    
    context = LLMContext(tools=all_tools)
    
    # declare turn strategies
    start_strategies = [
        #requires both, wake phrase blocks ALL stop strategies unless it is triggered, then allows other start strategy start frames to pass
        WakePhraseUserTurnStartStrategy(
            phrases=config.wake_phrases,
        ),
        VADUserTurnStartStrategy()]
    
    # no stop strategies / leave it blank in aggregator dec for defaults
    stop_strategies= []


    aggregators = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=vad_analyzer,
            user_turn_strategies=UserTurnStrategies(
                start=start_strategies,
            ),
        ),
    )
    return aggregators

# vLLM #
def create_llm_service():
    llm = OpenAILLMService(
        api_key=config.llm_api_key,
        base_url=config.llm_base_url,
        settings=OpenAILLMService.Settings(
            system_instruction=config.system_prompt,
            model=config.llm_model
        )
    )
    
    return llm


def create_tts_service():
    filters = []
    
    md_filter = MarkdownTextFilter(
        params=MarkdownTextFilter.InputParams(
            filter_code=config.md_filter_code,
            filter_tables=config.md_filter_tables,
            filter_repeated_sequences=config.md_filter_repeated_sequences
        )
    )
    filters.append(md_filter)
    
    chinese_filter = ChinesePunctuationFilter()
    if(config.ZH_filter_enabled):
        filters.append(chinese_filter)
        
    
    # # kokoro
    # tts = KokoroTTSService(
    #     model_path=config.kokoro_model_path,
    #     voices_path=config.kokoro_voice_path,
    #     text_filters=filters,
    #     settings=KokoroTTSService.Settings(
    #         voice=config.kokoro_voice,
    #         language=config.kokoro_language
    #     ),
    # )
    
    # piper
    tts = PiperTTSService(
        download_dir=config.piper_model_path,
        use_cuda=config.piper_use_cuda,
        text_filters=[md_filter],
        settings=PiperTTSService.Settings(
            voice=config.piper_voice,
        ),
    )
    
    return tts

def create_transport():
    transport = SingleClientWebsocketServerTransport(
        host=config.ws_host,
        port=config.ws_port,
        params=SingleClientWebsocketServerParams(
            audio_in_enabled=True,
            audio_in_sample_rate=config.audio_in_sample_rate,
            audio_out_enabled=True,
            audio_out_sample_rate=config.audio_out_sample_rate,
            serializer = ProtobufFrameSerializer()
        )
    )
    return transport

def create_frame_filter():
    types = (AudioRawFrame)
    frame_filter = FrameFilter(types=types)
    return frame_filter