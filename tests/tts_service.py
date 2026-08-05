from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# 台灣中文女聲
VOICE = "zh-TW-HsiaoYuNeural"

# 語速、音量、音高
RATE = "+0%"
VOLUME = "+0%"
PITCH = "+0Hz"


def speak(text: str) -> None:
    """將文字轉成台灣中文語音並立即播放。"""

    clean_text = text.strip()

    if not clean_text:
        print("沒有文字可以播放。")
        return

    # 找到目前虛擬環境中的 edge-playback.exe
    edge_playback = Path(sys.executable).with_name(
        "edge-playback.exe"
    )

    if not edge_playback.exists():
        raise FileNotFoundError(
            f"找不到 edge-playback.exe：{edge_playback}"
        )

    command = [
        str(edge_playback),
        "--voice",
        VOICE,
        "--rate",
        RATE,
        "--volume",
        VOLUME,
        "--pitch",
        PITCH,
        "--text",
        clean_text,
    ]

    print("正在播放：", clean_text)

    subprocess.run(
        command,
        check=True,
    )

    print("播放完成。")