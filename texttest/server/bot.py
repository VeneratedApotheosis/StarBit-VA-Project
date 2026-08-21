import asyncio
from fastapi import FastAPI, WebSocket
import uvicorn

from pipecat.workers.runner import WorkerRunner
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
)
from pipecat.serializers.protobuf import ProtobufFrameSerializer
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketTransport,
    FastAPIWebsocketParams,
)

import debug
import services

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 1. Accept the incoming WebSocket connection
    await websocket.accept()

    # 2. Instantiate transport directly with the accepted socket
    transport = FastAPIWebsocketTransport(
        websocket=websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=False,
            audio_out_enabled=False,
            serializer=ProtobufFrameSerializer(),
        )
    )

    context = services.create_llm_context()
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(context)
    
    llm = services.create_llm_service()
    printer = debug.LLMResponsePrinter()

    pipeline = Pipeline(
        [
            transport.input(),
            user_aggregator,
            llm,
            printer,
            transport.output(),
            assistant_aggregator,
        ]
    )

    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            # enable_metrics=True,
        ),
    )

    runner = WorkerRunner(handle_sigint=False)

    await runner.add_workers(worker)
    
    # 4. Run the worker process
    await runner.run()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=7860)