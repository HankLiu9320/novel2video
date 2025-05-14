import os
from moviepy.editor import VideoFileClip
from transnetv2 import TransNetV2


def split_video_scenes(video_path, output_dir="output_scenes"):
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
        output_path = os.path.join(output_dir, f"scene_{idx + 1}.mp4")

        # 输出视频参数设置
        scene_clip.write_videofile(
            output_path,
            codec="libx264",  # 通用编码格式
            audio_codec="aac",
            fps=video_clip.fps,
            threads=4  # 多线程加速
        )

    video_clip.close()


if __name__ == "__main__":
    video_path = "wudao.mp4"  # 替换为实际路径
    split_video_scenes(video_path)
