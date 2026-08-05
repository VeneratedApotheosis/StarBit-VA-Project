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

pyaudio_instance = pyaudio.PyAudio()

# config audio transport
transport = LocalAudioTransport(
    LocalAudioTransportParams(
        audio_in_enabled=True,
        audio_in_sample_rate=16000, # silero expects 8kHz or 16000Hz (16k recommended)
        audio_out_enabled=False,    # Set to True if you add TTS later
    )
)

async def main():
    return 1

if __name__ == "__main__":
    asyncio.run(main())