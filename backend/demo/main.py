import json

from backend.llm.openai import query_openai
from backend.util.file import read_file, write_file

# 原文
# story = read_file("story.txt")
# print(f"原文：{story}")
# print("============================================================")

# 拆分动态镜头
# input = story
# sys1 = read_file("prompt1.txt")
# openai = query_openai(input, sys1, 0.01)
# write_file(openai, "result1.txt")
# print(openai)
# print("============================================================")

# 优化提示词
result1 = read_file("result1.txt")
loads = json.loads(result1)

for storyboardObj in loads:
    print({storyboardObj["text"]})

    storyboardArr = storyboardObj["storyboard"]
    for storyboard in storyboardArr:
        print("\t", {storyboard["storyboard_text"]})
        print("\t", {storyboard["prompts"]})
