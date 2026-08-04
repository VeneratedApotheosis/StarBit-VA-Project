from pathlib import Path

import numpy as np
import torch
from scipy.io import wavfile
from silero_vad import (
    collect_chunks,
    get_speech_timestamps,
    load_silero_vad,
)

INPUT_FILE = Path("audio/test.wav")
OUTPUT_FILE = Path("audio/speech_only.wav")
SAMPLE_RATE = 16000


def load_wav(file_path: Path) -> torch.Tensor:
    """使用 scipy 讀取 WAV，不使用 TorchCodec。"""

    sample_rate, audio_data = wavfile.read(file_path)

    if sample_rate != SAMPLE_RATE:
        raise ValueError(
            f"錄音取樣率是 {sample_rate} Hz，"
            f"但程式需要 {SAMPLE_RATE} Hz。"
        )

    # 如果是雙聲道，轉成單聲道
    if audio_data.ndim == 2:
        audio_data = audio_data.mean(axis=1)

    # int16 轉成 -1 到 1 的浮點數
    if audio_data.dtype == np.int16:
        audio_data = audio_data.astype(np.float32) / 32768.0
    else:
        audio_data = audio_data.astype(np.float32)

    return torch.from_numpy(audio_data)


def save_wav(file_path: Path, audio_tensor: torch.Tensor) -> None:
    """將處理後的音訊儲存成 WAV。"""

    audio_numpy = audio_tensor.cpu().numpy()

    audio_numpy = np.clip(audio_numpy, -1.0, 1.0)
    audio_int16 = (audio_numpy * 32767).astype(np.int16)

    wavfile.write(
        file_path,
        SAMPLE_RATE,
        audio_int16,
    )


def detect_voice() -> None:
    if not INPUT_FILE.exists():
        print("找不到 audio/test.wav")
        print("請先輸入：python record.py")
        return

    print("正在載入 VAD 模型...")
    model = load_silero_vad()

    print("正在讀取錄音...")
    audio = load_wav(INPUT_FILE)

    print("正在偵測人聲...")
    speech_timestamps = get_speech_timestamps(
        audio,
        model,
        sampling_rate=SAMPLE_RATE,
    )

    if not speech_timestamps:
        print("沒有偵測到人聲。")
        print("請重新錄音，靠近麥克風並說話大聲一點。")
        return

    print("偵測到人聲區段：")

    for index, section in enumerate(speech_timestamps, start=1):
        start_seconds = section["start"] / SAMPLE_RATE
        end_seconds = section["end"] / SAMPLE_RATE

        print(
            f"第 {index} 段："
            f"{start_seconds:.2f} 秒到 "
            f"{end_seconds:.2f} 秒"
        )

    speech_audio = collect_chunks(
        speech_timestamps,
        audio,
    )

    save_wav(
        OUTPUT_FILE,
        speech_audio,
    )

    print("VAD 處理完成！")
    print(f"輸出檔案：{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    try:
        detect_voice()
    except Exception as error:
        print(f"執行失敗：{error}")