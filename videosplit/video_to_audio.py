# 安装依赖（需先安装FFmpeg环境）
from moviepy.editor import VideoFileClip

def extract_audio(video_path, audio_path="output_audio.mp3"):
    try:
        # 加载视频文件
        video = VideoFileClip(video_path)

        # 提取音频
        audio = video.audio

        # 保存音频文件
        audio.write_audiofile(audio_path, codec='libmp3lame', bitrate='192k')

        # 释放资源
        audio.close()
        video.close()
        print(f"音频提取成功：{audio_path}")
    except Exception as e:
        print(f"错误：{str(e)}")

# 使用示例
extract_audio("shipin.mp4", "extracted_audio.mp3")