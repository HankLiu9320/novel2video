from faster_whisper import WhisperModel

model_dir = "./audiomodels/fastwhisper/large-v3"  # 替换为实际路径

model_size = "large-v3"

# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
model = WhisperModel(model_dir, device="cpu", compute_type="int8", local_files_only=True)

segments, info = model.transcribe("extracted_audio.mp3", condition_on_previous_text=False, language="zh")

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
