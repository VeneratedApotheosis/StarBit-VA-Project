from pathlib import Path

from faster_whisper import WhisperModel


AUDIO_FILE = Path("audio/test.wav")


def speech_to_text() -> None:
    """將 VAD 處理後的語音轉換成文字。"""

    if not AUDIO_FILE.exists():
        print("找不到 audio/speech_only.wav")
        print("請先執行：python record.py")
        print("再執行：python vad_test.py")
        return

    print("正在載入 Whisper 模型...")

    model = WhisperModel(
        "small",
        device="cpu",
        compute_type="int8",
    )

    print("正在進行語音辨識...")

    segments, info = model.transcribe(
        str(AUDIO_FILE),
        language="zh",
        beam_size=5,
        vad_filter=False,
    )

    text_parts = []

    for segment in segments:
        text = segment.text.strip()

        if text:
            text_parts.append(text)

            print(
                f"[{segment.start:.2f} 秒 → "
                f"{segment.end:.2f} 秒] {text}"
            )

    final_text = "".join(text_parts)

    if not final_text:
        print("沒有辨識到文字。")
        return

    print("\n辨識結果：")
    print(final_text)

    output_file = Path("audio/result.txt")
    output_file.write_text(
        final_text,
        encoding="utf-8",
    )

    print(f"\n文字已儲存到：{output_file.resolve()}")


if __name__ == "__main__":
    try:
        speech_to_text()
    except Exception as error:
        print(f"執行失敗：{error}")