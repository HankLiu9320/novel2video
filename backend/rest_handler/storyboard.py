import json
import logging
import os
import shutil
from flask import request, jsonify

from backend.llm.llm import query_llm
from backend.util.constant import novel_storyboard_dir, novel_paragraphs_dir, character_dir
from backend.util.constant import prompt_path
from backend.util.file import read_file, write_file


# 分镜
def extract_storyboard_from_texts():
    try:
        if os.path.exists(novel_storyboard_dir):
            shutil.rmtree(novel_storyboard_dir)

        if not os.path.exists(novel_storyboard_dir):
            os.makedirs(novel_storyboard_dir)

        prompt = read_file(prompt_path)

        with open(os.path.join(character_dir, 'characters.txt'), 'r', encoding='utf-8') as file:
            character_map = json.load(file)
            names = [d['name'] for d in character_map.values()]
            # 将列表中的名字用逗号拼接成一个字符串
            names_string = ','.join(names)
            prompt = prompt.replace("%roles%", names_string)

        sorted_files_and_dirs = sorted(os.listdir(novel_paragraphs_dir))

        for file_name in sorted_files_and_dirs:
            lines = []
            with open(os.path.join(novel_paragraphs_dir, file_name), 'r', encoding='utf-8') as file:
                lines.extend(file.readlines())
            content = "".join(lines)
            res = query_llm(content, prompt, 1, 8192)
            file_path = os.path.join(novel_storyboard_dir, f"{file_name}.json")
            logging.info(f"storyboard_from_texts: {res}")
            write_file(res, file_path)

    except Exception as e:
        return jsonify({"error": "Failed to manage directory"}), 500


def update_storyboard():
    req = request.get_json()
    if (not req
            or 'fileName' not in req
            or 'paragraphIdx' not in req
            or 'storyboardIdx' not in req
            or 'type' not in req):
        return jsonify({"error": "parse request body failed"}), 400

    try:
        file_path = os.path.join(novel_storyboard_dir, f"{req['fileName']}")
        content = read_file(file_path)
        storyboard = json.loads(content)

        for item in storyboard:
            if item["index"] == req['paragraphIdx']:
                for subItem in item["storyboard"]:
                    if subItem["storyboard_index"] == req['storyboardIdx']:
                        # 修改 storyboard_text
                        subItem[req['type']] = req['content']
                        break  # 找到后可以退出内层循环

        with open(file_path, 'w') as file:
            json.dump(storyboard, file, ensure_ascii=False, indent=4)

    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to write file"}), 500

    return jsonify({"message": "Attachment saved successfully"}), 200
