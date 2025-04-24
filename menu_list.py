# 该代码用于从菜谱中提取有效信息

import json
import pandas as pd
import re

# 原始字符串列表（示例数据）
raw_input_list = ['```json\n[\n    {\n        "菜谱编号": 663731,\n        "菜名": "肉沫泡紫茄",\n        "卡路里": "600大卡",\n        "碳足迹": "0.4 千克二氧化碳当量",\n        "食材": [\n            "猪肉（200g）",\n            "紫皮茄子（2个）",\n            "姜（3片）",\n            "青辣椒（1个）",\n            "豆瓣酱（1勺）",\n            "耗油（1匙）",\n            "酱油（半匙）",\n            "花生油（2勺）",\n            "盐（半匙适量）",\n            "小米辣椒（1个）",\n            "洋葱（3块）",\n            "清水（5勺）"\n        ],\n        "蛋白质": "30g",\n        "脂肪": "40g",\n        "碳水化合物": "20g",\n        "纤维 素": "10g"\n    },\n    {\n        "菜谱编号": 663572,\n        "菜名": "酸菜炖粉条",\n        "卡路里": "500大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        "食材": [\n            "东北酸菜（400g）",\n            "猪肉（1块）",\n            "粉条（适量）",\n            "生抽（1匙）",\n            "葱姜片（少许）"\n        ],\n        "蛋白质": "25g",\n        "脂肪": "20g",\n        "碳水化合物": "60g",\n        "纤维素": "15g"\n    },\n    {\n        "菜谱编号": 663486,\n        "菜名": "大肚虾仁馄饨独家",\n        "卡路里": "700大卡",\n        "碳足迹": "0.6 千克二氧化碳当量",\n        "食材": [\n            "虾仁（8个）",\n            "猪肉馅（适量）",\n            "胡萝卜（1节）",\n            "食用油（1勺）",\n            "馄饨皮（适量）",\n            "盐（少许）",\n           "生抽（少许）"\n        ],\n        "蛋白质": "35g",\n        "脂肪": "30g",\n        "碳水化合物": "50g",\n        "纤维素": "5g"\n    }\n]\n```', '```json\n[\n    {\n        "菜谱编号": 663719,\n        "菜名": "低脂低卡银芽牛肉拌饭",\n        "卡路里": "350大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        " 食材": [\n            "绿豆芽（200g）",\n            "胡萝卜（1块）",\n            "牛肉沫（80g）",\n            "大米饭（100g）",\n            "小葱（1颗）",\n            "盐（1g）",\n            "白胡椒粉（1g）",\n            "生抽（1勺）",\n            "淀粉（拌肉）（0.25勺）",\n            "老抽（0.25勺）"\n        ],\n        "蛋白质": "25g",\n        "脂肪": "10g",\n        "碳水化合物": "50g",\n        "纤维素": "5g"\n    },\n    {\n        "菜谱编号": 663558,\n        " 菜名": "红焖牛肉",\n        "卡路里": "600大卡",\n        "碳足迹": "0.6 千克二氧化碳当量",\n        "食材": [\n            "牛肉（适量）",\n            "大葱段 （适量）",\n            "大料（1个）",\n            "花椒粉（适量）",\n            "香叶（2片）",\n            "白芷（2片）",\n            "桂皮（少许）",\n            "桅子（2个（上色作用））",\n            "干红椒（2个）",\n            "盐（适量）",\n            "生抽（适量）",\n            "红烧酱油（适量）",\n            "糖（1勺）",\n            "腐乳汁（适量）"\n        ],\n        "蛋白质": "40g",\n        "脂肪": "30g",\n        "碳水化合物": "20g",\n        "纤维素": "3g"\n    }\n]\n```', '```json\n[\n    {\n        "菜谱编号": 663062,\n        "菜名": "葱爆羊肉卷独家",\n        "卡路里": "600大卡",\n        "碳足迹": "0.4 千克二氧化碳当量",\n        "食材": [\n            "羊肉卷（适量）",\n            "大葱（适量）",\n            "香菜（适量）",\n            "胡椒粉（适量）",\n            "芝麻（适量）",\n            "姜（适量）",\n            "生抽（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "30g",\n        "脂肪": "20g",\n        "碳水化合物": "10g",\n        "纤维素": "2g"\n    },\n    {\n        "菜谱编号": 662950,\n        "菜名": "青萝卜全羊汤独家",\n        "卡路里": "500大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        "食材": [\n            "羊肉（适量）",\n            "羊杂（适量）",\n            "青萝卜（适量）",\n            "胡椒粉（适量）",\n            "水（适量）",\n            "姜（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "25g",\n        "脂 肪": "15g",\n        "碳水化合物": "15g",\n        "纤维素": "3g"\n    },\n    {\n        "菜谱编号": 662888,\n        "菜名": "羊肉水煎饺独家",\n        "卡路里": "700大卡",\n        "碳足迹": "0.5 千克二氧化碳当量",\n        "食材": [\n            "羊肉（适量）",\n            "面粉（适量）",\n            "香菜（适量）",\n            "胡萝卜（适量）",\n            "生抽（适量）",\n            "老抽（适量）",\n            "胡椒粉（适量）",\n            "五香粉（适量）",\n            "姜（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "35g",\n        "脂肪": "25g",\n        "碳水化合物": "80g",\n        "纤维素": "4g"\n    }\n]\n```']

def parse_recipe_data(raw_input_list):
    all_recipes = []
    for raw_block in raw_input_list:
        try:
            # 清理 markdown 外壳
            cleaned_block = raw_block.strip().lstrip("```json").rstrip("```").strip()
            recipes = json.loads(cleaned_block)
            all_recipes.extend(recipes)
        except Exception as e:
            print("解析失败：", e)

    # 提取主信息和食材信息
    main_info_list = []
    ingredient_rows = []

    for recipe in all_recipes:
        recipe_id = recipe.get("菜谱编号")
        name = recipe.get("菜名")
        calories = recipe.get("卡路里")
        carbon = recipe.get("碳足迹")
        protein = recipe.get("蛋白质")
        fat = recipe.get("脂肪")
        carb = recipe.get("碳水化合物")
        fiber = recipe.get("纤维素") or recipe.get("纤维 素")

        main_info_list.append({
            "菜谱编号": recipe_id,
            "菜名": name,
            "卡路里": calories,
            "碳足迹": carbon,
            "蛋白质": protein,
            "脂肪": fat,
            "碳水化合物": carb,
            "纤维素": fiber
        })

        for ing in recipe.get("食材", []):
            ingredient_rows.append({
                "菜谱编号": recipe_id,
                "菜名": name,
                "食材": ing.strip()
            })

    # 构建 DataFrame
    main_info_df = pd.DataFrame(main_info_list)
    ingredient_df = pd.DataFrame(ingredient_rows)

    # 拆分“食材”与“量”
    def split_ingredient(item):
        match = re.match(r'(.+?)（(.*?)）', item)
        if match:
            return match.group(1), match.group(2)
        else:
            return item, None

    ingredient_df["原始食材"] = ingredient_df["食材"]
    ingredient_df[["食材", "量"]] = ingredient_df["原始食材"].apply(lambda x: pd.Series(split_ingredient(x)))
    ingredient_df.drop(columns=["原始食材"], inplace=True)

    return main_info_df, ingredient_df

main_df, ing_df = parse_recipe_data(raw_input_list)

print("\n--- 主营养信息表 ---")
print(main_df)

print("\n--- 食材明细表（拆分） ---")
print(ing_df)

# 把ing_df纵表改成final_df长表
grouped = ing_df.groupby(['菜谱编号', '菜名'])['食材'].apply(list).reset_index()
ingredients_df = grouped['食材'].apply(pd.Series)
final_df = pd.concat([grouped[['菜谱编号', '菜名']], ingredients_df], axis=1)
ingredient_columns = final_df.columns[2:]
final_df["食材列表"] = final_df[ingredient_columns].apply(lambda row: row.dropna().tolist(), axis=1)

# 查看结果
print(final_df[["食材列表"]])
