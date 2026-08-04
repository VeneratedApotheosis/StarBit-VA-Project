import sounddevice as sd

print("目前可使用的音訊裝置：")
print(sd.query_devices())

print("\n預設裝置：")
print(sd.default.device)
