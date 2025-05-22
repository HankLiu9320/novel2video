import os
from moviepy.editor import VideoFileClip
from faster_whisper import WhisperModel
from backend.util.file import read_files_from_directory, read_file, write_file, append_file
from transnetv2 import TransNetV2

def split_videos():
    video_dir = "data/video_orginal"
    split_dir = "data/video_split"
    files = read_files_from_directory(video_dir)

    for idx, file in enumerate(files):
        file_path = os.path.join(video_dir, file)
        split_video_scenes(file_path, file_name=f"file{idx}", output_dir=split_dir)


def split_video_scenes(video_path, file_name="", output_dir="output_scenes"):
    # 初始化模型
    model = TransNetV2()

    # 预测视频镜头边界
    video_frames, single_frame_pred, all_frame_pred = model.predict_video(video_path)
    scenes = model.predictions_to_scenes(single_frame_pred)

    # 加载视频并分割
    video_clip = VideoFileClip(video_path)
    os.makedirs(output_dir, exist_ok=True)

    for idx, (start_frame, end_frame) in enumerate(scenes):
        # 计算时间戳（秒）
        start_time = start_frame / video_clip.fps
        end_time = end_frame / video_clip.fps

        # 提取镜头片段
        scene_clip = video_clip.subclip(start_time, end_time)
        output_path = os.path.join(output_dir, f"{file_name}_scene_{idx + 1}.mp4")

        # 输出视频参数设置
        scene_clip.write_videofile(
            output_path,
            codec="libx264",  # 通用编码格式
            audio_codec="aac",
            fps=video_clip.fps,
            threads=4  # 多线程加速
        )

    video_clip.close()


def extract_audios():
    video_dir = "data/video_orginal"
    audio_dir = "data/video_audio"
    files = read_files_from_directory(video_dir)

    for idx, file in enumerate(files):
        file_path = os.path.join(video_dir, file)
        basename = os.path.splitext(file)[0]
        extract_audio(file_path, audio_path=f"{audio_dir}/{basename}.mp3")


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


def extract_audio_text():
    model_dir = "./audiomodels/fastwhisper-model/large-v3"  # 替换为实际路径
    model_size = "large-v3"
    model = WhisperModel(model_dir, device="cpu", compute_type="int8", local_files_only=True)
    audio_dir = "data/video_audio"
    text_dir = "data/video_text"
    files = read_files_from_directory(audio_dir)

    for idx, file in enumerate(files):
        file_path = os.path.join(audio_dir, file)
        basename = os.path.splitext(file)[0]
        print(f"extract_audio_text:{file_path}")
        segments, info = model.transcribe(file_path, condition_on_previous_text=False, language="zh")
        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            append_file("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text), f"{text_dir}/{basename}.txt")

if __name__ == "__main__":
    # split_videos()
    # extract_audios();
    extract_audio_text()