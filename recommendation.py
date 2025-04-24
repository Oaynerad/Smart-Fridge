# 用于输出最终推荐菜单

import json
import pandas as pd
import ast
from menu_list import get_fridge_inventory
from ingredient_match import process_fridge_recipes

def recommend_recipes_from_fridge(raw_menue_list, fridge_ingredients_json_path, dish_amount):
    # 获取冰箱食材
    fridge_ingredients = get_fridge_inventory(fridge_ingredients_json_path)
    
    # 获取菜谱匹配结果
    final_df = process_fridge_recipes(fridge_ingredients_json_path, raw_menue_list)

    # 清理匹配字段格式
    def clean_match_list_column(x):
        if isinstance(x, str):
            try:
                parsed = ast.literal_eval(x)
            except Exception:
                return None
            if isinstance(parsed, list):
                return [None if i == 'None' else i for i in parsed]
            else:
                return None
        elif isinstance(x, list):
            return [None if i == 'None' else i for i in x]
        else:
            return None
    final_df["匹配冰箱食材"] = final_df["匹配冰箱食材"].apply(clean_match_list_column)

    # 转换None字符串为真正的None
    def convert_string_none_to_real_none(x):
        return [None if i == 'None' else i for i in x] if isinstance(x, list) else x
    final_df["匹配冰箱食材"] = final_df["匹配冰箱食材"].apply(convert_string_none_to_real_none)

    # 提取营养数据
    def safe_float_gram(val):
        if val is None or str(val).lower() == 'none':
            return 0.0
        return float(str(val).replace("g", "").strip())

    # 提取碳足迹
    def parse_carbon_footprint(val):
        try:
            return float(str(val).split()[0])
        except:
            return 0.0

    # 核心推荐函数
    def recommend_top_n_meals(final_df, fridge_df, top_n=3):
        recommendations = []

        for idx, row in final_df.iterrows():
            dish_id = row["菜谱编号"]
            dish_name = row["菜名"]
            match_list = row["匹配冰箱食材"]

            if not isinstance(match_list, list):
                continue

            freshness_score = 0
            feasible = False

            for item in match_list:
                if item is None or not isinstance(item, str):
                    continue
                matches = fridge_df[fridge_df["食材"] == item]
                if not matches.empty:
                    remaining = matches["保鲜剩余天数"].min()
                    if remaining < 0:
                        feasible = False
                        break
                    feasible = True
                    freshness_score += max(0, (7 - remaining))

            if not feasible:
                continue

            carbon_score = parse_carbon_footprint(row.get("碳足迹"))
            nutrition_score = (
                safe_float_gram(row.get("蛋白质")) +
                safe_float_gram(row.get("纤维素", row.get("纤维 素"))) -
                safe_float_gram(row.get("脂肪")) * 0.5
            )

            final_score = (
                0.5 * freshness_score +
                0.4 * nutrition_score -
                0.3 * carbon_score
            )

            recommendations.append((final_score, dish_id, dish_name))

        recommendations.sort(key=lambda x: -x[0])
        return recommendations[:top_n]

    recommendations = recommend_top_n_meals(final_df, fridge_ingredients, top_n=dish_amount)

    return recommendations

'''
# 调用示例
# 原始字符串列表（示例数据）
raw_menue_list = ['```json\n[\n    {\n        "菜谱编号": 663731,\n        "菜名": "肉沫泡紫茄",\n        "卡路里": "600大卡",\n        "碳足迹": "0.4 千克二氧化碳当量",\n        "食材": [\n            "猪肉（200g）",\n            "紫皮茄子（2个）",\n            "姜（3片）",\n            "青辣椒（1个）",\n            "豆瓣酱（1勺）",\n            "耗油（1匙）",\n            "酱油（半匙）",\n            "花生油（2勺）",\n            "盐（半匙适量）",\n            "小米辣椒（1个）",\n            "洋葱（3块）",\n            "清水（5勺）"\n        ],\n        "蛋白质": "30g",\n        "脂肪": "40g",\n        "碳水化合物": "20g",\n        "纤维 素": "10g"\n    },\n    {\n        "菜谱编号": 663572,\n        "菜名": "酸菜炖粉条",\n        "卡路里": "500大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        "食材": [\n            "东北酸菜（400g）",\n            "猪肉（1块）",\n            "粉条（适量）",\n            "生抽（1匙）",\n            "葱姜片（少许）"\n        ],\n        "蛋白质": "25g",\n        "脂肪": "20g",\n        "碳水化合物": "60g",\n        "纤维素": "15g"\n    },\n    {\n        "菜谱编号": 663486,\n        "菜名": "大肚虾仁馄饨独家",\n        "卡路里": "700大卡",\n        "碳足迹": "0.6 千克二氧化碳当量",\n        "食材": [\n            "虾仁（8个）",\n            "猪肉馅（适量）",\n            "胡萝卜（1节）",\n            "食用油（1勺）",\n            "馄饨皮（适量）",\n            "盐（少许）",\n           "生抽（少许）"\n        ],\n        "蛋白质": "35g",\n        "脂肪": "30g",\n        "碳水化合物": "50g",\n        "纤维素": "5g"\n    }\n]\n```', '```json\n[\n    {\n        "菜谱编号": 663719,\n        "菜名": "低脂低卡银芽牛肉拌饭",\n        "卡路里": "350大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        " 食材": [\n            "绿豆芽（200g）",\n            "胡萝卜（1块）",\n            "牛肉沫（80g）",\n            "大米饭（100g）",\n            "小葱（1颗）",\n            "盐（1g）",\n            "白胡椒粉（1g）",\n            "生抽（1勺）",\n            "淀粉（拌肉）（0.25勺）",\n            "老抽（0.25勺）"\n        ],\n        "蛋白质": "25g",\n        "脂肪": "10g",\n        "碳水化合物": "50g",\n        "纤维素": "5g"\n    },\n    {\n        "菜谱编号": 663558,\n        " 菜名": "红焖牛肉",\n        "卡路里": "600大卡",\n        "碳足迹": "0.6 千克二氧化碳当量",\n        "食材": [\n            "牛肉（适量）",\n            "大葱段 （适量）",\n            "大料（1个）",\n            "花椒粉（适量）",\n            "香叶（2片）",\n            "白芷（2片）",\n            "桂皮（少许）",\n            "桅子（2个（上色作用））",\n            "干红椒（2个）",\n            "盐（适量）",\n            "生抽（适量）",\n            "红烧酱油（适量）",\n            "糖（1勺）",\n            "腐乳汁（适量）"\n        ],\n        "蛋白质": "40g",\n        "脂肪": "30g",\n        "碳水化合物": "20g",\n        "纤维素": "3g"\n    }\n]\n```', '```json\n[\n    {\n        "菜谱编号": 663062,\n        "菜名": "葱爆羊肉卷独家",\n        "卡路里": "600大卡",\n        "碳足迹": "0.4 千克二氧化碳当量",\n        "食材": [\n            "羊肉卷（适量）",\n            "大葱（适量）",\n            "香菜（适量）",\n            "胡椒粉（适量）",\n            "芝麻（适量）",\n            "姜（适量）",\n            "生抽（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "30g",\n        "脂肪": "20g",\n        "碳水化合物": "10g",\n        "纤维素": "2g"\n    },\n    {\n        "菜谱编号": 662950,\n        "菜名": "青萝卜全羊汤独家",\n        "卡路里": "500大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        "食材": [\n            "羊肉（适量）",\n            "羊杂（适量）",\n            "青萝卜（适量）",\n            "胡椒粉（适量）",\n            "水（适量）",\n            "姜（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "25g",\n        "脂 肪": "15g",\n        "碳水化合物": "15g",\n        "纤维素": "3g"\n    },\n    {\n        "菜谱编号": 662888,\n        "菜名": "羊肉水煎饺独家",\n        "卡路里": "700大卡",\n        "碳足迹": "0.5 千克二氧化碳当量",\n        "食材": [\n            "羊肉（适量）",\n            "面粉（适量）",\n            "香菜（适量）",\n            "胡萝卜（适量）",\n            "生抽（适量）",\n            "老抽（适量）",\n            "胡椒粉（适量）",\n            "五香粉（适量）",\n            "姜（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "35g",\n        "脂肪": "25g",\n        "碳水化合物": "80g",\n        "纤维素": "4g"\n    }\n]\n```']
result = recommend_recipes_from_fridge(raw_menue_list, 'fridge_inventory.json', dish_amount=3)
for score, dish_id, dish_name in result:
    print(f"✅ 推荐：{dish_name}（菜谱编号：{dish_id}），优先级得分：{score:.2f}")
'''
