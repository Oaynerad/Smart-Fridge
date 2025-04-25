# 用于把菜谱内的原材料和冰箱内的库存对应

import json
import pandas as pd
import openai
import os
from tqdm import tqdm

# build GPT prompt
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

# from json get inventory in fridge
def get_fridge_inventory(json_file_path):
    # read JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # get ingredients and freshness_remaining
    items = data['items']
    records = [
        {"食材": name, "保鲜剩余天数": info.get("freshness_remaining", None)}
        for name, info in items.items()
    ]
    # transform to DataFrame
    fridge_ingredients = pd.DataFrame(records)
    return fridge_ingredients

# from list get main ingredients in dishes
def parse_recipe_data(file_path):

    # read JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    recipes = [item for sublist in raw_data if isinstance(sublist, list) for item in sublist]

    # build DataFrame
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
            "食材列表": recipe.get("食材"),
            "做法":recipe.get("做法步骤")
        })

    df = pd.DataFrame(df_records)
    return df, df.copy()

# match the ingredients of the dishes with inventory in fridge
def process_fridge_recipes(json_path, raw_menu_list):
    # 1. load fridge JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data['items']
    records = [
        {"食材": name, "保鲜剩余天数": info.get("freshness_remaining", None)}
        for name, info in items.items()
    ]
    fridge_ingredients = pd.DataFrame(records)

    # 2. get menu
    main_df, final_df = parse_recipe_data(raw_menu_list)

    # 3. create OpenAI client
    client = openai.OpenAI()

    # 4. match with inventory in fridge
    matched_names = []
    for _, row in tqdm(final_df.iterrows(), total=len(final_df)):
        match = gpt_match_main_ingredient(row["食材列表"], fridge_ingredients, client)
        matched_names.append(match if match != "None" else None)

    final_df["匹配冰箱食材"] = matched_names
    return final_df

'''final_df = process_fridge_recipes('fridge_inventory.json', "raw_menu_list.json")
print(final_df)'''
