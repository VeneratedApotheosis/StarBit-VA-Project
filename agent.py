from pathlib import Path
from openai import OpenAI

# 建立 OpenAI 客戶端
client = OpenAI()

# 語音辨識後的文字檔
RESULT_FILE = Path("audio/result.txt")

if not RESULT_FILE.exists():
    print("找不到 audio/result.txt")
    raise SystemExit

# 讀取你剛剛說的內容
user_text = RESULT_FILE.read_text(encoding="utf-8").strip()

if not user_text:
    print("result.txt 裡面沒有文字")
    raise SystemExit

print("你說：")
print(user_text)

print("\nAI 正在思考...")

response = client.responses.create(
    model="gpt-4.1-mini",
    instructions=(
        "你是一個中文 AI 語音助理。"
        "請使用繁體中文回答，內容簡單、自然，不要太長。"
    ),
    input=user_text
)

answer = response.output_text

print("\nAI 回答：")
print(answer)

Path("audio/answer.txt").write_text(
    answer,
    encoding="utf-8"
)

print("\n回答已儲存到 audio/answer.txt")