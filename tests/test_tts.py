from tts_service import speak


def main() -> None:
    print("Microsoft 台灣中文 TTS 測試")
    print("輸入 exit 可以結束程式。")

    while True:
        text = input("\n請輸入要朗讀的文字：").strip()

        if text.lower() == "exit":
            print("程式結束。")
            break

        if not text:
            print("請輸入文字。")
            continue

        try:
            speak(text)

        except Exception as error:
            print("TTS 執行失敗：", error)


if __name__ == "__main__":
    main()