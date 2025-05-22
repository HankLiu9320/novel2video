import os
from faster_whisper import WhisperModel
from faster_whisper import batcher
import ffmpeg
from datetime import timedelta

def extract_subtitles(mp3_path, srt_path="output.srt", model_size="large-v2"):
    try:
        # 初始化模型
        model = WhisperModel(
            model_size,
            device="cuda",  # 可选 "cpu" 或 "mps"（Mac）
            compute_type="float16"  # GPU加速需设置此项
        )

        # 加载音频并转换采样率
        audio = model.load_audio(mp3_path)
        audio = audio.set_frame_rate(16000)

        # 分段处理音频（提升准确性）
        segments = []
        for segment in batcher(audio, model.chunk_length_sec):
            result = model.transcribe_segment(
                segment,
                beam_size=5,
                initial_prompt=None,
                word_timestamps=True  # 启用单词级时间戳
            )
            segments.extend(result[0].segments)

        # 生成SRT字幕
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments):
                start = str(timedelta(seconds=seg.start))
                end = str(timedelta(seconds=seg.end))
                text = seg.text.replace("\n", " ")
                f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")

        print(f"成功生成 {len(segments)} 条字幕到 {srt_path}")

    except Exception as e:
        print(f"错误：{str(e)}")
        return False
    return True

# 使用示例
if __name__ == "__main__":
    input_mp3 = "extracted_audio.mp3"
    output_srt = "subtitle.srt"

    # 自动转换MP3为WAV（若需要）
    if not input_mp3.endswith(".wav"):
        ffmpeg.input(input_mp3).output("temp.wav", acodec="pcm_s16le").run()
        input_mp3 = "temp.wav"

    extract_subtitles(input_mp3, output_srt)