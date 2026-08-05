import asyncio
from fastapi import FastAPI, WebSocket

from pipecat.pipeline.pipeline import Pipeline
from pipecat.workers.runner import WorkerRunner
from pipecat.pipeline.worker import PipelineParams, PipelineWorker

from pipecat.observers.loggers.transcription_log_observer import TranscriptionLogObserver
from pipecat.observers.loggers.debug_log_observer import DebugLogObserver
from pipecat.frames.frames import LLMTextFrame, TranscriptionFrame

from pipecat.services.ollama.llm import OLLamaLLMService
from pipecat.transports.websocket.fastapi import FastAPIWebsocketTransport, FastAPIWebsocketParams
from pipecat.serializers.protobuf import ProtobufFrameSerializer

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Define text-only WebSocket transport
    transport = FastAPIWebsocketTransport(
        websocket=websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=False,
            audio_out_enabled=False,
            serializer=ProtobufFrameSerializer(),
        )
    )

    # Configure OLLama Service
    llm = OLLamaLLMService(
        settings=OLLamaLLMService.Settings(
            model="llama3.2",
        )
    )

    # pipeline declaration with text input and output transport layers
    pipeline = Pipeline([
        transport.input(),   # Receives text frames from client
        llm,                 # Generates LLM response frames
        transport.output(),  # Sends text frames back to client
    ])

    observers = [
        # catches and logs TranscriptionFrame outputs
        TranscriptionLogObserver(),

        # catches and logs specified frames 
        DebugLogObserver(frame_types=(LLMTextFrame, TranscriptionFrame))
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