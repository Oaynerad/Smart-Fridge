# 用于把菜谱内的原材料和冰箱内的库存对应

import json
import pandas as pd
import openai
import os
from tqdm import tqdm

# 调用GPT的prompt
def gpt_match_main_ingredient(ingredient, fridge_ingredients, client):
    prompt = f"""你是一位智能厨房助理。请判断下面这道菜的主料（忽略括号里的食材数量）是否是“冰箱中已有的食材”，即：
- 是冰箱中已有的某种食材（即使名称有差异，但意义相同，比如紫皮茄子->茄子）
- 同时它是该菜谱中的主要食材，而不是调味品或配料

冰箱中目前有以下食材：{fridge_ingredients["食材"].tolist()}
菜谱中主料：{ingredient}

请你判断该菜谱中的主料是否匹配冰箱中的某种食材？若是，请返回匹配的冰箱食材名称；若不是主料或没有匹配项，请返回“None”，返回时请按这一格式：[东北酸菜, 猪肉, None, None, None]。
"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# 从json中获取冰箱的食材
def get_fridge_inventory(json_file_path):
    # 读取 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 提取食材及其 freshness_remaining
    items = data['items']
    records = [
        {"食材": name, "保鲜剩余天数": info.get("freshness_remaining", None)}
        for name, info in items.items()
    ]
    # 转为 DataFrame
    fridge_ingredients = pd.DataFrame(records)
    return fridge_ingredients

# 从list中获得菜谱中的主料
def parse_recipe_data(file_path):

    # 读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 展开每一个子列表中的字典
    recipes = [item for sublist in raw_data if isinstance(sublist, list) for item in sublist]

    # 构建 DataFrame
    df_records = []
    for recipe in recipes:
        df_records.append({
            "菜谱编号": recipe.get("菜谱编号"),
            "菜名": recipe.get("菜名"),
            "卡路里": recipe.get("卡路里"),
            "碳足迹": recipe.get("碳足迹"),
            "蛋白质": recipe.get("蛋白质"),
            "脂肪": recipe.get("脂肪"),
            "碳水化合物": recipe.get("碳水化合物"),
            "纤维素": recipe.get("纤维素"),
            "食材列表": recipe.get("食材")
        })

    df = pd.DataFrame(df_records)
    return df, df.copy()

# 调用GPT对菜谱中的主料和冰箱的食材进行匹配
def process_fridge_recipes(json_path, raw_menu_list):
    # 1. 加载冰箱 JSON 文件
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data['items']
    records = [
        {"食材": name, "保鲜剩余天数": info.get("freshness_remaining", None)}
        for name, info in items.items()
    ]
    fridge_ingredients = pd.DataFrame(records)

    # 2. 解析菜谱数据
    main_df, final_df = parse_recipe_data(raw_menu_list)

    # 3. 创建 OpenAI 客户端
    client = openai.OpenAI()

    # 4. 匹配冰箱主料
    matched_names = []
    for _, row in tqdm(final_df.iterrows(), total=len(final_df)):
        match = gpt_match_main_ingredient(row["食材列表"], fridge_ingredients, client)
        matched_names.append(match if match != "None" else None)

    final_df["匹配冰箱食材"] = matched_names
    return final_df

'''final_df = process_fridge_recipes('fridge_inventory.json', "raw_menu_list.json")
print(final_df)'''