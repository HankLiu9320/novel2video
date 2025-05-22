# 安装依赖（需GPU加速建议安装CUDA版）
import ssl
from unittest import result

import whisper
import soundfile as sf
from datetime import timedelta


def speech_to_subtitle(audio_path, srt_path="output.srt", model_size="base"):
    # 加载音频
    audio, sr = sf.read(audio_path)

    # 初始化 Whisper 模型
    model = whisper.load_model(model_size, download_root="./audiomodels")
    # model = whisper.load_model(model_size)
    print("====1=====")

    # 语音识别
    result = model.transcribe(audio, fp16=False)
    print("====2=====")
    print(result)

    # 生成 SRT 字幕
    subtitles = []
    for i, segment in enumerate(result["segments"]):
        start = str(timedelta(seconds=segment["start"]))
        end = str(timedelta(seconds=segment["end"]))
        text = segment["text"].strip()

        subtitles.append(f"{i + 1}\n{start} --> {end}\n{text}\n")

    # 保存文件
    with open(srt_path, "w", encoding="utf-8") as f:
        f.writelines(subtitles)

    print(f"生成 {len(subtitles)} 条语音字幕")
    return subtitles


# 使用示例
context = ssl._create_unverified_context()
speech_to_subtitle("extracted_audio.mp3")
