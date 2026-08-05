from pipecat.services.kokoro.tts import KokoroTTSService


# 喇叭播放的取樣率
SAMPLE_RATE = 24000


def create_tts() -> KokoroTTSService:
    """建立免費、本機執行的中文 Kokoro TTS。"""

    return KokoroTTSService(
        settings=KokoroTTSService.Settings(
            voice="zf_xiaobei",
            language="cmn",
        ),
    )