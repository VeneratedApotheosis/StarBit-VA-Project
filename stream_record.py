import queue

import numpy as np
import sounddevice as sd


fs = 16000
block_size = 1600

audio_queue = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    """每收到一小段麥克風聲音，就放進佇列。"""

    if status:
        print("麥克風狀態：", status)

    audio_queue.put(indata.copy())


print("開始持續收音，按 Ctrl+C 停止。")

try:
    with sd.InputStream(
        samplerate=fs,
        channels=1,
        dtype="int16",
        blocksize=block_size,
        callback=audio_callback,
    ):
        while True:
            audio_chunk = audio_queue.get()

            volume = np.sqrt(
                np.mean(audio_chunk.astype(np.float32) ** 2)
            )

            if volume > 500:
                print("偵測到說話，音量：", int(volume))

except KeyboardInterrupt:
    print("\n已停止收音。")

except Exception as error:
    print("發生錯誤：", error)