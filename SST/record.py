import sounddevice as sd
from scipy.io.wavfile import write

fs = 16000
seconds = 5

print("開始錄音，請說話...")

recording = sd.rec(
    int(seconds * fs),
    samplerate=fs,
    channels=1,
    dtype='int16'
)

sd.wait()

write("audio/test.wav", fs, recording)

print("錄音完成！")