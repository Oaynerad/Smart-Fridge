# 用于把菜谱内的原材料和冰箱内的库存对应

import json
import pandas as pd
import openai
import os
from tqdm import tqdm
from menu_list import parse_recipe_data

def gpt_match_main_ingredient(ingredient, fridge_ingredients, client):
    prompt = f"""你是一位智能厨房助理。请判断下面这道菜的食材（忽略括号里的食材数量）是否是“冰箱中已有的主料”，即：
- 是冰箱中已有的某种食材（即使名称有差异，但意义相同，比如紫皮茄子->茄子）
- 同时它是该菜谱中的主要食材，而不是调味品或配料

冰箱中目前有以下食材：{fridge_ingredients["食材"].tolist()}
菜谱中食材：{ingredient}

请你判断该菜谱中的食材是否匹配冰箱中的某种主料？若是，请返回匹配的冰箱食材名称；若不是主料或没有匹配项，请返回“None”，返回时请按这一格式：[东北酸菜, 猪肉, None, None, None]。
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

def parse_recipe_data(raw_menu_list):
    import re
    import ast

    recipes = []
    for raw in raw_menu_list:
        json_text = re.search(r'```json\n(.*?)```', raw, re.DOTALL)
        if json_text:
            parsed = json.loads(json_text.group(1))
            recipes.extend(parsed)

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

'''raw_menue_list = ['```json\n[\n    {\n        "菜谱编号": 663731,\n        "菜名": "肉沫泡紫茄",\n        "卡路里": "600大卡",\n        "碳足迹": "0.4 千克二氧化碳当量",\n        "食材": [\n            "猪肉（200g）",\n            "紫皮茄子（2个）",\n            "姜（3片）",\n            "青辣椒（1个）",\n            "豆瓣酱（1勺）",\n            "耗油（1匙）",\n            "酱油（半匙）",\n            "花生油（2勺）",\n            "盐（半匙适量）",\n            "小米辣椒（1个）",\n            "洋葱（3块）",\n            "清水（5勺）"\n        ],\n        "蛋白质": "30g",\n        "脂肪": "40g",\n        "碳水化合物": "20g",\n        "纤维 素": "10g"\n    },\n    {\n        "菜谱编号": 663572,\n        "菜名": "酸菜炖粉条",\n        "卡路里": "500大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        "食材": [\n            "东北酸菜（400g）",\n            "猪肉（1块）",\n            "粉条（适量）",\n            "生抽（1匙）",\n            "葱姜片（少许）"\n        ],\n        "蛋白质": "25g",\n        "脂肪": "20g",\n        "碳水化合物": "60g",\n        "纤维素": "15g"\n    },\n    {\n        "菜谱编号": 663486,\n        "菜名": "大肚虾仁馄饨独家",\n        "卡路里": "700大卡",\n        "碳足迹": "0.6 千克二氧化碳当量",\n        "食材": [\n            "虾仁（8个）",\n            "猪肉馅（适量）",\n            "胡萝卜（1节）",\n            "食用油（1勺）",\n            "馄饨皮（适量）",\n            "盐（少许）",\n           "生抽（少许）"\n        ],\n        "蛋白质": "35g",\n        "脂肪": "30g",\n        "碳水化合物": "50g",\n        "纤维素": "5g"\n    }\n]\n```', '```json\n[\n    {\n        "菜谱编号": 663719,\n        "菜名": "低脂低卡银芽牛肉拌饭",\n        "卡路里": "350大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        " 食材": [\n            "绿豆芽（200g）",\n            "胡萝卜（1块）",\n            "牛肉沫（80g）",\n            "大米饭（100g）",\n            "小葱（1颗）",\n            "盐（1g）",\n            "白胡椒粉（1g）",\n            "生抽（1勺）",\n            "淀粉（拌肉）（0.25勺）",\n            "老抽（0.25勺）"\n        ],\n        "蛋白质": "25g",\n        "脂肪": "10g",\n        "碳水化合物": "50g",\n        "纤维素": "5g"\n    },\n    {\n        "菜谱编号": 663558,\n        " 菜名": "红焖牛肉",\n        "卡路里": "600大卡",\n        "碳足迹": "0.6 千克二氧化碳当量",\n        "食材": [\n            "牛肉（适量）",\n            "大葱段 （适量）",\n            "大料（1个）",\n            "花椒粉（适量）",\n            "香叶（2片）",\n            "白芷（2片）",\n            "桂皮（少许）",\n            "桅子（2个（上色作用））",\n            "干红椒（2个）",\n            "盐（适量）",\n            "生抽（适量）",\n            "红烧酱油（适量）",\n            "糖（1勺）",\n            "腐乳汁（适量）"\n        ],\n        "蛋白质": "40g",\n        "脂肪": "30g",\n        "碳水化合物": "20g",\n        "纤维素": "3g"\n    }\n]\n```', '```json\n[\n    {\n        "菜谱编号": 663062,\n        "菜名": "葱爆羊肉卷独家",\n        "卡路里": "600大卡",\n        "碳足迹": "0.4 千克二氧化碳当量",\n        "食材": [\n            "羊肉卷（适量）",\n            "大葱（适量）",\n            "香菜（适量）",\n            "胡椒粉（适量）",\n            "芝麻（适量）",\n            "姜（适量）",\n            "生抽（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "30g",\n        "脂肪": "20g",\n        "碳水化合物": "10g",\n        "纤维素": "2g"\n    },\n    {\n        "菜谱编号": 662950,\n        "菜名": "青萝卜全羊汤独家",\n        "卡路里": "500大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        "食材": [\n            "羊肉（适量）",\n            "羊杂（适量）",\n            "青萝卜（适量）",\n            "胡椒粉（适量）",\n            "水（适量）",\n            "姜（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "25g",\n        "脂 肪": "15g",\n        "碳水化合物": "15g",\n        "纤维素": "3g"\n    },\n    {\n        "菜谱编号": 662888,\n        "菜名": "羊肉水煎饺独家",\n        "卡路里": "700大卡",\n        "碳足迹": "0.5 千克二氧化碳当量",\n        "食材": [\n            "羊肉（适量）",\n            "面粉（适量）",\n            "香菜（适量）",\n            "胡萝卜（适量）",\n            "生抽（适量）",\n            "老抽（适量）",\n            "胡椒粉（适量）",\n            "五香粉（适量）",\n            "姜（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "35g",\n        "脂肪": "25g",\n        "碳水化合物": "80g",\n        "纤维素": "4g"\n    }\n]\n```']

final_df = process_fridge_recipes('fridge_inventory.json', raw_menue_list)
final_df.to_json("test_df.json", force_ascii=False, orient="records", indent=2)'''
