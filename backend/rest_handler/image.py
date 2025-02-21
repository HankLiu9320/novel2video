import asyncio
import json
import logging
import os
import re

from flask import jsonify, request

from backend.image.image import generate_image, generate_images_single
from backend.util.constant import image_dir, image_storyboard_dir, novel_storyboard_dir, image_role_dir, character_dir, \
    characters_path
from backend.util.file import make_dir, remove_all, read_files_from_directory, read_file


def handle_error(message, err):
    return jsonify({"error": message}), 500

async def async_generate_images(lines):
    try:
        await generate_image(lines)
    except Exception as e:
        logging.error(e)
        raise e


async def async_generate_image_single(content, name, outdir):
    try:
        await generate_images_single(content, name, outdir)
    except Exception as e:
        logging.error(e)
        raise

def generate_role_images():
    try:
        remove_all(image_role_dir)
        make_dir(image_role_dir)
    except Exception as e:
        return handle_error("Failed to manage directory", e)
    try:
        file_path = os.path.join(character_dir, characters_path)
        characters = read_file(file_path)
        data = json.loads(characters)

        for character in data:
            name = character;
            jdata = data[character];
            prompts = jdata.get('prompts', '')
            outdir = "role/"
            file = os.path.join("/images", outdir, name + '.png')
            asyncio.run(generate_images_single(prompts, name, outdir))
            data[character]['imgUrl'] = file

            with open(file_path, 'w') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)


    except Exception as e:
        return handle_error("Failed to read fragments", e)
    return jsonify({"status": "Image generation started"}), 200


def generate_images():
    try:
        remove_all(image_storyboard_dir)
        make_dir(image_storyboard_dir)
    except Exception as e:
        return handle_error("Failed to manage directory", e)
    try:
        files = read_files_from_directory(novel_storyboard_dir)
        data = []
        fileIdx = 0;

        for file in files:
            file_path = os.path.join(novel_storyboard_dir, file)
            storyboard = read_file(file_path)
            data = json.loads(storyboard)
            storyboardObjIdx = 0;

            for storyboardObj in data:
                storyboards = storyboardObj["storyboard"]

                itemIdx = 0;
                for storyboardItem in storyboards:
                    print(storyboardItem["storyboard_text"], storyboardItem["prompts"])
                    content = storyboardItem["prompts"]
                    name = f"{fileIdx}-{storyboardObjIdx}-{itemIdx}"
                    outdir = "storyboard/"
                    file = os.path.join("/images", outdir, name + '.png')
                    asyncio.run(generate_images_single(content, name, outdir))
                    data[storyboardObjIdx]['storyboard'][itemIdx]['storyboard_image'] = file

                    with open(file_path, 'w') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)

                    itemIdx += 1

                storyboardObjIdx += 1

            fileIdx += 1

        # if err:
        #     return handle_error("Failed to read fragments", err)
        # asyncio.run(async_generate_images(lines))
    except Exception as e:
        return handle_error("Failed to read fragments", e)
    return jsonify({"status": "Image generation started"}), 200

def get_local_images():
    try:
        files = os.listdir(image_dir)
    except Exception as e:
        return jsonify({"error": "Failed to read image directory"}), 500

    image_map = {}
    for file in files:
        if not os.path.isdir(file):
            matches = re.match(r'(\d+)\.png', file)
            if matches:
                key = matches.group(1)
                abs_path = os.path.join("/images", file)
                image_map[key] = abs_path

    return jsonify(image_map), 200

def generate_single_image():
    try:
        req = request.get_json()
        if not req or 'name' not in req or 'content' not in req:
            return jsonify({"error": "parse request body failed"}), 400
        file = os.path.join("/images", str(req['outdir']), str(req['name'])+'.png')
        logging.info(f"file:{file}")
        asyncio.run(async_generate_image_single(req['content'], req['name'], req['outdir']))
    except Exception as e:
        return handle_error("Failed to read fragments", e)
    return jsonify({"status": "Image generation started", "url":file}), 200
