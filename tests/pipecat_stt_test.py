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

# 1. config audio transport
transport = LocalAudioTransport(
    LocalAudioTransportParams(
        audio_in_enabled=True,
        audio_in_sample_rate=16000, # silero expects 8kHz or 16000Hz (16k recommended)
        audio_out_enabled=False,    # Set to True if you add TTS later
    )
)

# 2. config whisper using settings
stt = WhisperSTTService(
        settings=WhisperSTTService.Settings(
            # options: TINY, BASE, SMALL, MEDIUM, LARGE_V3_TURBO
        model=Model.BASE.value, 

        # select lang
        language=Language.ZH_TW,    
        
        # probability threshold to filter out silence/background noise
        no_speech_prob=0.4,      
    ),

    # hardware configuration
    device="gpu", # gpu / cpu
    compute_type="int8",   # int8 / float16 to optimize memory
)

# 3. config silero vad
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

vad_processor = VADProcessor(vad_analyzer=vad_analyzer)

async def main():
    #pipeline declaration
    pipeline = Pipeline([
        transport.input(),
        vad_processor,
        stt,
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