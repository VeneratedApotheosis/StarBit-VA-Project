import asyncio

import sounddevice as sd
from pipecat.evals.speech import EvalSpeech

from tts_service import SAMPLE_RATE, create_tts


async def main() -> None:
    text = input("請輸入要朗讀的文字：").strip()

    if not text:
        print("沒有輸入文字。")
        return

    print("正在載入 Kokoro TTS...")

    tts = create_tts()

    try:
        # EvalSpeech 會替 TTS 建立：
        # TaskManager、Clock、StartFrame 和 sample rate。
        async with EvalSpeech(
            tts,
            sample_rate=SAMPLE_RATE,
            cache_key="kokoro-zf-xiaobei-cmn",
            use_cache=False,
        ) as speech:
            print("正在產生語音...")

            pcm_audio, actual_sample_rate = await speech.generate(text)

        print("實際取樣率：", actual_sample_rate)
        print("音訊大小：", len(pcm_audio), "bytes")
        print("開始播放語音...")

        with sd.RawOutputStream(
            samplerate=actual_sample_rate,
            channels=1,
            dtype="int16",
        ) as speaker:
            speaker.write(pcm_audio)

        print("語音播放完成！")

    except Exception as error:
        print("TTS 執行失敗：", error)


if __name__ == "__main__":
    asyncio.run(main())