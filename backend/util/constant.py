import os
from pathlib import Path

base_dir = os.path.join(os.getcwd(), "temp")

image_dir = os.path.join(base_dir, "image")
character_dir = os.path.join(base_dir, "character")
novel_fragments_dir = os.path.join(base_dir, "fragments")
novel_storyboard_dir = os.path.join(base_dir, "storyboard")
prompts_dir = os.path.join(base_dir, "prompts")
prompts_en_dir = os.path.join(base_dir, "promptsEn")
audio_dir = os.path.join(base_dir, "audio")
video_dir = os.path.join(base_dir, "video")
novel_path = "novel.txt"
role_prompt_path = "role_prompt.txt"
prompt_path = "prompt.txt"
config_path = "config.json"