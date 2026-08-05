import asyncio

import sounddevice as sd
from pipecat.frames.frames import ErrorFrame, TTSAudioRawFrame

from tts_service import SAMPLE_RATE, create_tts


async def main() -> None:
    text = input("請輸入要朗讀的文字：").strip()

    if not text:
        print("沒有輸入文字。")
        return

    print("正在載入 Kokoro TTS...")
    tts = create_tts()

    print("開始產生並播放語音...")

    try:
        with sd.RawOutputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
        ) as speaker:

            async for frame in tts.run_tts(
                text,
                context_id="local-tts-test",
            ):
                if isinstance(frame, TTSAudioRawFrame):
                    speaker.write(frame.audio)

                elif isinstance(frame, ErrorFrame):
                    raise RuntimeError(frame.error)

        print("語音播放完成！")

    except Exception as error:
        print("TTS 執行失敗：", error)


if __name__ == "__main__":
    asyncio.run(main())