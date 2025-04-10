import json

from backend.llm.openai import query_openai
from backend.util.file import read_file, write_file
import re

def getJsonData(content: str):
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

# 原文
# story = read_file("story.txt")
# print(f"原文：{story}")
# print("============================================================")

# 角色提取
# input = story
# sys1 = read_file("prompt0.txt")
# openai = query_openai(input, sys1, 0.01)
# write_file(openai, "result0.txt")
# print(openai)
# print("==========================角色提取==================================")

# 拆分段落
# input = story
# sys1 = read_file("prompt1.txt")
# openai = query_openai(input, sys1, 0.01)
# res = getJsonData(openai)
# with open("data.json", 'w', encoding='utf-8') as file:
#     json.dump(res, file, ensure_ascii=False, indent=4)
# write_file(res, "result1.txt")
# print(res)
# print("=========================拆分段落===================================")


# 拆分动态镜头
# sys2 = read_file("prompt2.txt")
# with open("data.json", 'r', encoding='utf-8') as file:
#     globalRes = json.load(file)
#
# for globalResItem in globalRes:
#     text = globalResItem["段落原文"]
#     print(text)
#     openai = query_openai(text, sys2, 0.01)
#     res = getJsonData(openai)
#     arr = []
#
#     for idx, r in enumerate(res):
#         data = {
#             "id": idx,
#             "镜头文本": r
#         }
#         arr.append(data)
#     globalResItem["镜头列表"] = arr
# with open("data.json", 'w', encoding='utf-8') as file:
#     json.dump(globalRes, file, ensure_ascii=False, indent=4)
# print("===========================拆分动态镜头=================================")

# 静态画面拆分
sys3 = read_file("prompt3.txt")
with open("data.json", 'r', encoding='utf-8') as file:
    globalRes = json.load(file)

for globalResItem in globalRes:
    duanluoText = globalResItem["段落原文"]
    jingtouList = globalResItem["镜头列表"]

    for jingtouItem in jingtouList:
        print(duanluoText)
        print(jingtouItem["镜头文本"])
        sys3 = sys3.format(duanluoText)
        openai = query_openai(jingtouItem["镜头文本"], sys3, 0.01)
        res = getJsonData(openai)
        print(res)
        arr = []

        for idx, r in enumerate(res):
            data = {
                "id": idx,
                "画面文本": r
            }
            arr.append(data)

        jingtouItem["画面列表"] = arr
with open("data.json", 'w', encoding='utf-8') as file:
    json.dump(globalRes, file, ensure_ascii=False, indent=4)
print("===========================静态画面拆分=================================")


# 优化提示词
# result1 = read_file("result1.txt")
# loads = json.loads(result1)
#
# for storyboardObj in loads:
#     print({storyboardObj["text"]})
#
#     storyboardArr = storyboardObj["storyboard"]
#     for storyboard in storyboardArr:
#         print("\t", {storyboard["storyboard_text"]})
#         print("\t", {storyboard["prompts"]})


