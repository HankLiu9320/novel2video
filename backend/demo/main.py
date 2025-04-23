import json

from backend.llm.openai import query_openai
from backend.util.file import read_file, write_file
import re


def get_json_data(content: str):
    pattern = r'```json\n(.*?)\n```'  # 匹配以```json包裹的代码块
    match = re.search(pattern, content, re.DOTALL)  # re.DOTALL允许跨行匹配

    if match:
        json_str = match.group(1)
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            print(f"JSON解析错误：{e}")
    else:
        data = json.loads(content)
        return data


def read_story():
    # 原文
    story = read_file("story.txt")
    print(f"原文：{story}")
    print("============================================================")
    return story


# 角色提取
def extract_roles(story: str):
    input = story
    sys1 = read_file("prompt0.txt")
    content, reasoning_content = query_openai(input, sys1, 0.01)
    print(f"content:{content}")
    print(f"reasoning_content:{reasoning_content}")
    write_file(content, "result0.txt")
    print("==========================角色提取==================================")


# 拆分段落 "prompt1.txt"
def split_paragraph(story: str, prompt_file: str, res_file: str):
    input = story
    sys1 = read_file(prompt_file)
    content, reasoning_content = query_openai(input, sys1, 0.01)
    print(f"content:{content}")
    print(f"reasoning_content:{reasoning_content}")
    res = get_json_data(content)
    with open(res_file, 'w', encoding='utf-8') as file:
        json.dump(res, file, ensure_ascii=False, indent=4)

    print("=========================拆分段落===================================")


# 拆分动态镜头 "prompt2.txt"
def split_dynamic_lens(prompt_file: str, res_file: str):
    sys2 = read_file(prompt_file)
    with open(res_file, 'r', encoding='utf-8') as file:
        globalRes = json.load(file)

    for globalResItem in globalRes:
        text = globalResItem["段落原文"]
        print(f"段落原文:{text}")
        content, reasoning_content = query_openai(text, sys2, 0.01)
        print(f"content:{content}")
        print(f"reasoning_content:{reasoning_content}")
        res = get_json_data(content)
        arr = []

        for idx, r in enumerate(res):
            data = {
                "id": idx,
                "镜头文本": r
            }
            arr.append(data)
        globalResItem["镜头列表"] = arr

        with open(res_file, 'w', encoding='utf-8') as file:
            json.dump(globalRes, file, ensure_ascii=False, indent=4)
    print("===========================拆分动态镜头=================================")


# 静态画面拆分 "prompt3.txt"
def split_static_lens(prompt_file: str, res_file: str):
    sys3 = read_file(prompt_file)
    keys = read_file("keys.txt")

    with open(res_file, 'r', encoding='utf-8') as file:
        globalRes = json.load(file)

    for globalResItem in globalRes:
        duanluoText = globalResItem["段落原文"]
        jingtouList = globalResItem["镜头列表"]

        for jingtouItem in jingtouList:
            print(r"段落原文:{}", duanluoText)
            print(r"镜头文本:{}", jingtouItem["镜头文本"])
            p3 = sys3.replace("{段落原文}", duanluoText)
            p3 = p3.replace("{提示词}", keys)

            content, reasoning_content = query_openai(jingtouItem["镜头文本"], p3, 0.01)
            print(r"content:{}", content)
            print(r"reasoning_content:{}", reasoning_content)
            res = get_json_data(content)
            arr = []

            for idx, r in enumerate(res):
                data = {
                    "id": idx,
                    "画面文本": r["画面文本"],
                    "画面背景": r["画面背景"],
                    "prompts": r["prompts"]
                }
                arr.append(data)

            jingtouItem["画面列表"] = arr

            with open(res_file, 'w', encoding='utf-8') as file:
                json.dump(globalRes, file, ensure_ascii=False, indent=4)
    print("===========================静态画面拆分=================================")


if __name__ == '__main__':
    # story = read_story()
    # extract_roles(story)
    # split_paragraph(story=story, prompt_file="prompt1.txt", res_file="data.json")
    # split_dynamic_lens(prompt_file="prompt2.txt", res_file="data.json")
    split_static_lens(prompt_file="prompt3.txt", res_file="data.json")
