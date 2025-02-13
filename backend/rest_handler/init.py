import json
import logging
import os

from flask import request, jsonify

from backend.util.constant import image_dir, novel_path, prompts_dir, prompts_en_dir, prompt_path, \
    config_path, role_prompt_path, novel_paragraphs_dir, novel_storyboard_dir
from backend.util.file import read_files_from_directory, read_lines_from_directory, read_file, \
    read_lines_from_directory_utf8, write_file


def handle_error(status_code, message, error):
    response = jsonify({'error': message, 'details': str(error)})
    response.status_code = status_code
    return response


def get_initial():
    try:
        files = read_files_from_directory(novel_storyboard_dir)
        data = []

        for file in files:
            file_path = os.path.join(novel_storyboard_dir, file)
            storyboard = read_file(file_path)
            item = {}
            item["file"] = file
            item["storyboards"] = json.loads(storyboard)
            data.append(item)
            print(f"storyboard:{storyboard}")

    except Exception as e:
        logging.error(e)
        return handle_error(500, "Failed to process request", e)

    return jsonify(data), 200


def load_novel():
    try:
        content = read_file(novel_path)
        return jsonify({'content': content}), 200
    except FileNotFoundError:
        return jsonify({'content': ''}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def save_novel():
    try:
        data = request.get_json()
        content = data.get('content', '')

        with open(novel_path, 'w', encoding='utf-8') as file:
            file.write(content)

        chunks = split_text(content)
        fileIndex = 1

        for i, chunk in enumerate(chunks):
            print(f"chunk:{chunk}")
            file_path = os.path.join(novel_paragraphs_dir, f"{fileIndex}.txt")
            write_file(chunk, file_path)
            fileIndex += 1

        return jsonify({'message': '保存成功！'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def split_text(text, chunk_size=500):
    start = 0
    chunks = []

    while start < len(text):
        # 确定截取的结束位置（起始位置加上chunk_size）
        end = start + chunk_size
        if end >= len(text):
            # 如果剩余文本长度不足chunk_size，直接加入剩余文本
            chunks.append(text[start:])
            break

        # 在chunk_size后的文本中查找第一个句号
        period_index = text.find('。', end)

        if period_index == -1:
            # 如果找不到句号，则直接加入剩余文本
            chunks.append(text[start:])
            break

        # 截取到句号的位置
        chunks.append(text[start:period_index + 1])

        # 更新起始位置为下一个句号后的字符
        start = period_index + 1

    return chunks

def load_prompt():
    try:
        content = read_file(prompt_path)
        return jsonify({'content': content}), 200
    except FileNotFoundError:
        return jsonify({'content': ''}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def save_prompt():
    try:
        data = request.get_json()
        content = data.get('content', '')

        with open(prompt_path, 'w', encoding='utf-8') as file:
            file.write(content)

        return jsonify({'message': '保存成功！'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def load_role_prompt():
    try:
        content = read_file(role_prompt_path)
        return jsonify({'content': content}), 200
    except FileNotFoundError:
        return jsonify({'content': ''}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def save_role_prompt():
    try:
        data = request.get_json()
        content = data.get('content', '')

        with open(role_prompt_path, 'w', encoding='utf-8') as file:
            file.write(content)

        return jsonify({'message': '保存成功！'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_model_config():
    if not os.path.exists(config_path) or os.path.getsize(config_path) == 0:
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump({'model': '', 'url': '', 'apikey': '', 'address2': '', 'address3': ''}, file)
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logging.info(data['url'])
        return jsonify(data)
    except Exception as e:
        logging.error(f'Error reading addresses: {e}')
        return 'Error reading addresses', 500


def save_model_config():
    try:
        data = request.json
        key = data.get('key')
        value = data.get('value')
        with open(config_path, 'r', encoding='utf-8') as file:
            addresses = json.load(file)
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass  # If it's not a JSON string, keep it as is
        addresses[key] = value
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(addresses, file, ensure_ascii=False, indent=4)
        return 'Address saved successfully', 200
    except Exception as e:
        logging.error(f'Error saving {key}: {e}')
        return f'Error saving {key}', 500
