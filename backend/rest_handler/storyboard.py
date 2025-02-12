import logging
import os
import shutil

from flask import jsonify

from backend.llm.llm import query_llm
from backend.util.constant import novel_path, novel_storyboard_dir
from backend.util.constant import prompt_path
from backend.util.file import read_file


# 分镜
def extract_storyboard_from_texts():
    try:
        if not os.path.exists(novel_storyboard_dir):
            os.makedirs(novel_storyboard_dir)

        if os.path.exists(novel_storyboard_dir):
            shutil.rmtree(novel_storyboard_dir)

        prompt = read_file(prompt_path)
        content = read_file(novel_path)
        res = query_llm(content, prompt, 1, 8192)
        logging.info(f"storyboard_from_texts: {res}")

    except Exception as e:
        return jsonify({"error": "Failed to manage directory"}), 500
