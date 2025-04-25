import pandas as pd
from ingredient_match import get_fridge_inventory
from ingredient_match import process_fridge_recipes
import json
import re
import openai

# 辅助函数

def parse_carbon_footprint(carbon_str): # 碳足迹数据处理为数字
    try:
        return float(carbon_str.split(" ")[0])
    except:
        return 0.0

def safe_float_gram(s): # 营养成分数据处理为数字
    try:
        return float(s.lower().replace("g", "").replace("约", ""))
    except:
        return 0.0

def force_parse_to_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            # 把无引号的词（如 胡萝卜）变成加引号的："胡萝卜"
            x_fixed = re.sub(r'(?<!["\'])\b([\u4e00-\u9fa5\w]+)\b(?!["\'])', r'"\1"', x)
            # 把 None 换成 null
            x_fixed = x_fixed.replace("None", "null")
            # 用 json.loads 来解析
            return json.loads(x_fixed)
        except Exception as e:
            print(f"无法解析: {x} -> {e}")
            return []
    return []

# 推荐函数
def recommend_top_n_meals(final_df, fridge_df, top_n=3):
    recommendations = []
    final_df["匹配冰箱食材"] = final_df["匹配冰箱食材"].apply(force_parse_to_list)
    
    for idx, row in final_df.iterrows():
        dish_id = row["菜谱编号"]
        dish_name = row["菜名"]
        match_list = row["匹配冰箱食材"]
        cook_method = row["做法"]
 
        if not isinstance(match_list, list):
            print('Error! Match_list is not a list')
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

        recommendations.append((final_score, dish_id, dish_name, cook_method))

    recommendations.sort(key=lambda x: -x[0])
    return recommendations[:top_n]

# 菜名翻译函数
def translate_dish_names(results, client):
    translated_results = []

    for score, dish_id, dish_name, cook_method  in results:
        # 构造 prompt
        prompt = f"请将下面的菜名翻译成英文，仅返回英文名称，不需要解释，也不要加其他字符：\n\n{dish_name}"

        # 调用 GPT API
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # 可根据你账号实际模型权限修改
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        # 获取翻译结果
        translated_name = response.choices[0].message.content.strip()
        translated_results.append((score, dish_id, translated_name, cook_method))

    return translated_results

def recommend_recipes_from_fridge(raw_menu_path, fridge_inventory_path, dish_amount):
    fridge_df = get_fridge_inventory(fridge_inventory_path)
    final_df = process_fridge_recipes(fridge_inventory_path, raw_menu_path)
    recommendations = recommend_top_n_meals(final_df, fridge_df, dish_amount)
    client = openai.OpenAI()
    translated = translate_dish_names(recommendations, client)
    return translated

# 调用示例
'''result = recommend_recipes_from_fridge('raw_menu_list.json', 'fridge_inventory.json',3)
for score, dish_id, dish_name in result:
    print(f"✅ 推荐：{dish_name}（菜谱编号：{dish_id}），优先级得分：{score:.2f}")'''
