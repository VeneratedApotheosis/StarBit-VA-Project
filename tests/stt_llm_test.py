import asyncio
import pyaudio

import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.services.whisper.stt import WhisperSTTService, Model
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.transcriptions.language import Language

from pipecat.frames.frames import (
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    TranscriptionFrame,
)
from pipecat.frames.frames import Frame, TextFrame
from pipecat.services.ollama.llm import OLLamaLLMService

from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)

from pipecat.pipeline.pipeline import Pipeline
from pipecat.workers.runner import WorkerRunner
from pipecat.pipeline.worker import PipelineParams, PipelineWorker

from pipecat.observers.loggers.transcription_log_observer import (
    TranscriptionLogObserver,
)
from pipecat.observers.loggers.debug_log_observer import DebugLogObserver
from pipecat.frames.frames import (
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
    TextFrame,
)

from pipecat.transports.local.audio import (
    LocalAudioTransport,
    LocalAudioTransportParams,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from pipecat.transports.base_transport import BaseTransport

load_dotenv(override=True)


class Config:
    # Whisper Stuff
    WHISPER_LANGUAGE = Language.ZH_TW
    WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda")
    WHISPER_MODEL = Model.MEDIUM.value
    WHISPER_COMPUTE_TYPE = "default"  # default / int8 / float16 to optimize memory

    # VAD Stuff
    VAD_CONFIDENCE = 0.7
    VAD_STOP_SECS = 0.8
    VAD_START_SECS = 0.1
    MIN_VOLUME = 0.6

    # LLM stuff
    LLM_MODEL = "llama3.2"

    # Static pipeline constants
    AUDIO_SAMPLE_RATE = 16000


def create_stt_service() -> WhisperSTTService:
    # config whisper using settings
    stt = WhisperSTTService(
        settings=WhisperSTTService.Settings(
            # options: TINY, BASE, SMALL, MEDIUM, LARGE_V3_TURBO
            # instaalled: base, medium
            model=Config.WHISPER_MODEL,
            # select lang
            language=Config.WHISPER_LANGUAGE,
            # probability threshold to filter out silence/background noise
            no_speech_prob=0.4,
        ),
        # hardware configuration
        device=Config.WHISPER_DEVICE,  # cuda / cpu | requires cublas installation for cuda
        compute_type="float16",
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


def create_llm_service():
    # configure llm service
    llm = OLLamaLLMService(
        settings=OLLamaLLMService.Settings(
            model=Config.LLM_MODEL,
        )
    )
    return llm

# debug
class TextPrinter(FrameProcessor):
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, TextFrame):
            print(f"[TEXT]: {frame.text}")
        await self.push_frame(frame, direction)

class LLMResponsePrinter(FrameProcessor):
    def __init__(self):
        super().__init__()
        self._buffer = []

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        
        if isinstance(frame, TextFrame):
            self._buffer.append(frame.text)
        
        # print and clear buffer when LLM finishes generation
        elif isinstance(frame, LLMFullResponseEndFrame):
            full_text = "".join(self._buffer)
            print(f"[LLM OUTPUT]: {full_text}")
            self._buffer.clear()

        # pass the original frame downstream
        await self.push_frame(frame, direction)

# debug

async def run_bot(transport: BaseTransport) -> None:

    stt = create_stt_service()
    vad_analyzer = create_vad_analyzer()
    vad_processor = VADProcessor(vad_analyzer=vad_analyzer)

    context = LLMContext()
    aggregators = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=vad_analyzer),
    )

    llm = create_llm_service()

    # declare pipeline
    pipeline = Pipeline(
        [
            transport.input(),
            vad_processor,
            stt,
            aggregators.user(),
            llm,
            LLMResponsePrinter(),
            aggregators.assistant(),
        ]
    )

    # declare observers
    observers = [
        # catches and logs TranscriptionFrame outputs
        TranscriptionLogObserver(),
        # catches and logs VAD output frames (UserStartedSpeakingFrame / UserStoppedSpeakingFrame)
        # text frames
        DebugLogObserver(
            frame_types=(
                UserStartedSpeakingFrame,
                UserStoppedSpeakingFrame,
            )
        ),
    ]

    # declare work and runner
    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            vad_analyzer=vad_analyzer,
            observers=observers,
        ),
    )

    runner = WorkerRunner(handle_sigint=False)

    await runner.add_workers(worker)

    try:
        print("Starting pipeline... Press Ctrl+C to stop.")
        await runner.run()

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        pass


async def main():
    # config audio transport
    transport = LocalAudioTransport(
        LocalAudioTransportParams(
            audio_in_enabled=True,
            audio_in_sample_rate=Config.AUDIO_SAMPLE_RATE,  # silero expects 8kHz or 16000Hz (16k recommended)
            audio_out_enabled=False,  # Set to True if you add TTS later
        )
    )

    await run_bot(transport)


if __name__ == "__main__":
    asyncio.run(main())
