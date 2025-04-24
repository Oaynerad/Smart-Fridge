# 这个代码用于比对菜谱里材料和冰箱内材料的情况

import json
import pandas as pd
import openai
import os
from tqdm import tqdm
from menu_list import parse_recipe_data

# 读取 JSON 文件
with open('fridge_inventory.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取食材及其 freshness_remaining
items = data['items']
records = [
    {"食材": name, "保鲜剩余天数": info.get("freshness_remaining", None)}
    for name, info in items.items()
]

# 转为 DataFrame
fridge_ingredients = pd.DataFrame(records)

# 设置 API 密钥
client = openai.OpenAI()

# 测试用菜谱json
raw_input_list = ['```json\n[\n    {\n        "菜谱编号": 663731,\n        "菜名": "肉沫泡紫茄",\n        "卡路里": "600大卡",\n        "碳足迹": "0.4 千克二氧化碳当量",\n        "食材": [\n            "猪肉（200g）",\n            "紫皮茄子（2个）",\n            "姜（3片）",\n            "青辣椒（1个）",\n            "豆瓣酱（1勺）",\n            "耗油（1匙）",\n            "酱油（半匙）",\n            "花生油（2勺）",\n            "盐（半匙适量）",\n            "小米辣椒（1个）",\n            "洋葱（3块）",\n            "清水（5勺）"\n        ],\n        "蛋白质": "30g",\n        "脂肪": "40g",\n        "碳水化合物": "20g",\n        "纤维 素": "10g"\n    },\n    {\n        "菜谱编号": 663572,\n        "菜名": "酸菜炖粉条",\n        "卡路里": "500大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        "食材": [\n            "东北酸菜（400g）",\n            "猪肉（1块）",\n            "粉条（适量）",\n            "生抽（1匙）",\n            "葱姜片（少许）"\n        ],\n        "蛋白质": "25g",\n        "脂肪": "20g",\n        "碳水化合物": "60g",\n        "纤维素": "15g"\n    },\n    {\n        "菜谱编号": 663486,\n        "菜名": "大肚虾仁馄饨独家",\n        "卡路里": "700大卡",\n        "碳足迹": "0.6 千克二氧化碳当量",\n        "食材": [\n            "虾仁（8个）",\n            "猪肉馅（适量）",\n            "胡萝卜（1节）",\n            "食用油（1勺）",\n            "馄饨皮（适量）",\n            "盐（少许）",\n           "生抽（少许）"\n        ],\n        "蛋白质": "35g",\n        "脂肪": "30g",\n        "碳水化合物": "50g",\n        "纤维素": "5g"\n    }\n]\n```', '```json\n[\n    {\n        "菜谱编号": 663719,\n        "菜名": "低脂低卡银芽牛肉拌饭",\n        "卡路里": "350大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        " 食材": [\n            "绿豆芽（200g）",\n            "胡萝卜（1块）",\n            "牛肉沫（80g）",\n            "大米饭（100g）",\n            "小葱（1颗）",\n            "盐（1g）",\n            "白胡椒粉（1g）",\n            "生抽（1勺）",\n            "淀粉（拌肉）（0.25勺）",\n            "老抽（0.25勺）"\n        ],\n        "蛋白质": "25g",\n        "脂肪": "10g",\n        "碳水化合物": "50g",\n        "纤维素": "5g"\n    },\n    {\n        "菜谱编号": 663558,\n        " 菜名": "红焖牛肉",\n        "卡路里": "600大卡",\n        "碳足迹": "0.6 千克二氧化碳当量",\n        "食材": [\n            "牛肉（适量）",\n            "大葱段 （适量）",\n            "大料（1个）",\n            "花椒粉（适量）",\n            "香叶（2片）",\n            "白芷（2片）",\n            "桂皮（少许）",\n            "桅子（2个（上色作用））",\n            "干红椒（2个）",\n            "盐（适量）",\n            "生抽（适量）",\n            "红烧酱油（适量）",\n            "糖（1勺）",\n            "腐乳汁（适量）"\n        ],\n        "蛋白质": "40g",\n        "脂肪": "30g",\n        "碳水化合物": "20g",\n        "纤维素": "3g"\n    }\n]\n```', '```json\n[\n    {\n        "菜谱编号": 663062,\n        "菜名": "葱爆羊肉卷独家",\n        "卡路里": "600大卡",\n        "碳足迹": "0.4 千克二氧化碳当量",\n        "食材": [\n            "羊肉卷（适量）",\n            "大葱（适量）",\n            "香菜（适量）",\n            "胡椒粉（适量）",\n            "芝麻（适量）",\n            "姜（适量）",\n            "生抽（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "30g",\n        "脂肪": "20g",\n        "碳水化合物": "10g",\n        "纤维素": "2g"\n    },\n    {\n        "菜谱编号": 662950,\n        "菜名": "青萝卜全羊汤独家",\n        "卡路里": "500大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        "食材": [\n            "羊肉（适量）",\n            "羊杂（适量）",\n            "青萝卜（适量）",\n            "胡椒粉（适量）",\n            "水（适量）",\n            "姜（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "25g",\n        "脂 肪": "15g",\n        "碳水化合物": "15g",\n        "纤维素": "3g"\n    },\n    {\n        "菜谱编号": 662888,\n        "菜名": "羊肉水煎饺独家",\n        "卡路里": "700大卡",\n        "碳足迹": "0.5 千克二氧化碳当量",\n        "食材": [\n            "羊肉（适量）",\n            "面粉（适量）",\n            "香菜（适量）",\n            "胡萝卜（适量）",\n            "生抽（适量）",\n            "老抽（适量）",\n            "胡椒粉（适量）",\n            "五香粉（适量）",\n            "姜（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "35g",\n        "脂肪": "25g",\n        "碳水化合物": "80g",\n        "纤维素": "4g"\n    }\n]\n```']
# 食材明细表 ing_df 示例（你应替换为实际的 DataFrame）
main_df, ing_df = parse_recipe_data(raw_input_list)

# 处理菜谱原料格式
grouped = ing_df.groupby(['菜谱编号', '菜名'])['食材'].apply(list).reset_index()
ingredients_df = grouped['食材'].apply(pd.Series)
final_df = pd.concat([grouped[['菜谱编号', '菜名']], ingredients_df], axis=1)
ingredient_columns = final_df.columns[2:]
final_df["食材列表"] = final_df[ingredient_columns].apply(lambda row: row.dropna().tolist(), axis=1)

# 定义 GPT 比对函数（集成是否是主料 + 是否匹配冰箱）
def gpt_match_main_ingredient(ingredient, fridge_ingredients):
    prompt = f"""你是一位智能厨房助理。请判断下面这道菜的食材是否是“冰箱中已有的主料”，即：
- 是冰箱中已有的某种食材（即使名称有差异，但意义相同，比如紫皮茄子->茄子）
- 同时它是该菜谱中的主要食材，而不是调味品或配料

冰箱中目前有以下食材：{fridge_ingredients["食材"].tolist()}
菜谱中食材：{ingredient}

请你判断该菜谱中的食材是否匹配冰箱中的某种主料？若是，请返回匹配的冰箱食材名称；若不是主料或没有匹配项，请返回“None”，返回时请按这一格式：[东北酸菜, 猪肉, None, None, None]。
"""
    print(prompt)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# 遍历每一行进行匹配
matched_names = []
for _, row in tqdm(final_df.iterrows(), total=len(final_df)):
    match = gpt_match_main_ingredient(row["食材列表"], fridge_ingredients)
    matched_names.append(match if match != "None" else None)

# 添加新列并显示
final_df["匹配冰箱食材"] = matched_names
print(final_df)
