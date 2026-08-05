import asyncio
import pyaudio

from pipecat.services.whisper.stt import WhisperSTTService, Model
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.transcriptions.language import Language

from pipecat.pipeline.pipeline import Pipeline
from pipecat.workers.runner import WorkerRunner
from pipecat.pipeline.worker import PipelineParams, PipelineWorker

from pipecat.observers.loggers.transcription_log_observer import TranscriptionLogObserver
from pipecat.observers.loggers.debug_log_observer import DebugLogObserver
from pipecat.frames.frames import UserStartedSpeakingFrame, UserStoppedSpeakingFrame

from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams


from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.transports.base_transport import BaseTransport


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments) -> None:

    # 1. config whisper using settings
    stt = WhisperSTTService(
        settings=WhisperSTTService.Settings(
                # options: TINY, BASE, SMALL, MEDIUM, LARGE_V3_TURBO
                # instaalled: base, medium
            model=Model.MEDIUM.value, 

            # select lang
            language=Language.ZH_TW,    
            
            # probability threshold to filter out silence/background noise
            no_speech_prob=0.4,      
        ),

        # hardware configuration
        device="auto", # cuda / cpu | requires cublas installation for cuda
        compute_type="float16",   # int8 / float16 to optimize memory
    )

    # 2. config silero vad
    vad_analyzer = SileroVADAnalyzer(
        params=VADParams(
            # lower if bot ignores quiet speakers.
            # raise if background noise triggers the bot
            confidence=0.7,   
            
            # how much continuous speech is needed to trigger a turn
            start_secs=0.2,   

            # how much silence required to consider a turn complete
            stop_secs=0.8,    
        )
    )

    # 3. declare vad processor
    vad_processor = VADProcessor(vad_analyzer=vad_analyzer)
