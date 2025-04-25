from smart_fridge_tracker import get_display_names_from_file
import openai

keyword = get_display_names_from_file("fridge_inventory.json")


def translate_keywords_with_gpt(keywords, client):
    # 将列表合并成逗号分隔的字符串供 GPT 处理
    keyword_str = "，".join(keywords)

    prompt = f"""你是一位专业翻译，请将下面的中文食材名称列表翻译为英文，保持原顺序。
输入：{keyword_str}
输出格式：['英文1', '英文2', '英文3', ...]，只返回这行内容，不要添加任何说明或解释。"""

    # 调用 GPT API
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # 你可以用 gpt-4.0 或 gpt-3.5-turbo 等
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # 获取内容并转为 Python 列表
    translated_str = response.choices[0].message.content.strip()

    try:
        # 安全地将字符串格式的列表转换为 Python 列表
        translated_keywords = eval(translated_str)
    except Exception as e:
        print("⚠️ 翻译结果解析失败：", translated_str)
        raise e

    return translated_keywords

'''client = openai.OpenAI()
translated_keywords = translate_keywords_with_gpt(keyword, client)
print(translated_keywords)'''