from backend.util.file import get_config
from openai import OpenAI


def query_openai(input_text: str, sys: str, temperature: float) -> str:
    try:
        key = get_config()['apikey']
        url = get_config()['url']
        model = get_config()['model']
        print(f"query openai:{url},{model}")
        client = OpenAI(api_key=key, base_url=url)
        messages = []
        if sys:
            messages.append({"role": "system", "content": sys})
        messages.append({"role": "user", "content": input_text})

        # deepseek-chat
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=False
        )

        print(f"response: {response}")
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred when querying llm: {e}")
        raise
