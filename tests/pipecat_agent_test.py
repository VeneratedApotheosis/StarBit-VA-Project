import asyncio

from pipecat.pipeline.pipeline import Pipeline
from pipecat.workers.runner import WorkerRunner
from pipecat.pipeline.worker import PipelineParams, PipelineWorker

from pipecat.observers.loggers.transcription_log_observer import TranscriptionLogObserver
from pipecat.observers.loggers.debug_log_observer import DebugLogObserver

from pipecat.services.ollama import OLLamaLLMService, OLLamaLLMSettings

llm = OLLamaLLMService(
    model="llama3.2",
)

async def main():
    #pipeline declaration
    pipeline = Pipeline([
        llm,
    ])

    observers = [
        # catches and logs TranscriptionFrame outputs
        TranscriptionLogObserver(),

        # catches and logs specified frames 
        DebugLogObserver(frame_types=())
    ]

    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
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