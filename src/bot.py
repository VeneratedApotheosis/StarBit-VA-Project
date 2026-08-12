import asyncio

from pipecat.processors.audio.vad_processor import VADProcessor

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
)

from pipecat.transports.local.audio import (
    LocalAudioTransport,
    LocalAudioTransportParams,
)

from pipecat.transports.base_transport import BaseTransport

from config import Config
from debug import LLMResponsePrinter
import services

async def run_bot(transport: BaseTransport) -> None:

    stt = services.create_stt_service()
    vad_analyzer = services.create_vad_analyzer()
    vad_processor = VADProcessor(vad_analyzer=vad_analyzer)

    context = services.create_llm_context()
    aggregators = services.create_llm_aggregators(context,vad_analyzer)

    llm = services.create_llm_service()
    tts = services.create_tts_service()

    # declare pipeline
    pipeline = Pipeline(
        [
            transport.input(),
            vad_processor,
            stt,
            aggregators.user(),
            llm,
            LLMResponsePrinter(),
            tts,
            transport.output(),
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
            # enable_metrics=True,
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
            audio_out_enabled=True,
            audio_out_sample_rate=Config.AUDIO_SAMPLE_RATE,
        )
    )

    await run_bot(transport)


if __name__ == "__main__":
    asyncio.run(main())
