$project = "C:\Users\Jeff Sun\Desktop\work\StarBit-VA-Project"

# 避免 NLTK / regex 的安全路徑問題
$env:PYTHONSAFEPATH = "1"

# 告訴 Python 去 tests 資料夾尋找 tts_service.py
$env:PYTHONPATH = "$project\tests"

# 切換到專案外的暫存資料夾
Set-Location $env:TEMP

# 執行 TTS 測試程式
& "$project\.venv\Scripts\python.exe" -P "$project\tests\test_tts.py"