import asyncio

from pipecat.pipeline.pipeline import Pipeline
from pipecat.workers.runner import WorkerRunner
from pipecat.pipeline.worker import PipelineParams, PipelineWorker

from pipecat.observers.loggers.transcription_log_observer import TranscriptionLogObserver
from pipecat.observers.loggers.debug_log_observer import DebugLogObserver

async def main():
    #pipeline declaration
    pipeline = Pipeline([
    ])

    observers = [
        # catches and logs TranscriptionFrame outputs
        TranscriptionLogObserver(),

        # catches and logs VAD output frames (UserStartedSpeakingFrame / UserStoppedSpeakingFrame)
        DebugLogObserver(frame_types=(UserStartedSpeakingFrame, UserStoppedSpeakingFrame))
    ]

    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            vad_analyzer=vad_analyzer, 
            observers=observers,
        )
    )

    runner = WorkerRunner()

    await runner.add_workers(worker)

    try:
        print("Starting pipeline... Press Ctrl+C to stop.")
        await runner.run()
        
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        pass

if __name__ == "__main__":
    asyncio.run(main())