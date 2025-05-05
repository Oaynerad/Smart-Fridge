import pandas as pd
from ingredient_match import get_fridge_inventory
from ingredient_match import process_fridge_recipes
import json
import re
import openai

# sup function

def parse_carbon_footprint(carbon_str): # carbon footprint to float
    try:
        return float(carbon_str.split(" ")[0])
    except:
        return 0.0

def safe_float_gram(s): # nutrition to float
    try:
        return float(s.lower().replace("g", "").replace("约", ""))
    except:
        return 0.0

def force_parse_to_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            # add ""
            x_fixed = re.sub(r'(?<!["\'])\b([\u4e00-\u9fa5\w]+)\b(?!["\'])', r'"\1"', x)
            # change None to null
            x_fixed = x_fixed.replace("None", "null")
            # use json.loads
            return json.loads(x_fixed)
        except Exception as e:
            print(f"无法解析: {x} -> {e}")
            return []
    return []

# recommendation function
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

# translation function
def translate_dish_names(results, client):
    translated_results = []

    for score, dish_id, dish_name, cook_method in results:
        # build prompt
        prompt = f"""你是一名专业中英文翻译，请将下列中文翻译为英文：
1. 菜名：{dish_name}
2. 烹饪方式：{cook_method}

请分别翻译这两个内容，仅返回英文翻译的结果，格式如下：
<菜名英文>
<烹饪方式英文>
不要添加其他说明。
### Example：
 "Steamed Eggs"
 "Cooking Method: Wash the eggs and place them in the egg steamer. Add an appropriate amount of water to the water level line of the steamer based on the number of eggs you want to steam. Cover the steamer, connect the power, and start steaming. Wait for the steamer to finish its work; generally, let it sit for a while after the indicator light goes off. Be careful of steam burns when opening the lid. After steaming, remove the eggs, and mix 1 to 2 grams of salt, 3 to 5 drops of dark soy sauce, and 2 to 3 drops of sesame oil in a small bowl. Pour the mixture over the eggs, then sprinkle with 1 to 2 grams of chopped cilantro and green onions."
"""

        # GPT API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        # result of translation
        content = response.choices[0].message.content.strip()
        lines = content.split("\n")
        translated_name = lines[0].strip()
        translated_method = lines[1].strip() if len(lines) > 1 else ""

        translated_results.append((score, dish_id, translated_name, translated_method))

    return translated_results

def recommend_recipes_from_fridge(raw_menu_path, fridge_inventory_path, dish_amount):
    fridge_df = get_fridge_inventory(fridge_inventory_path)
    final_df = process_fridge_recipes(fridge_inventory_path, raw_menu_path)
    recommendations = recommend_top_n_meals(final_df, fridge_df, dish_amount)
    client = openai.OpenAI()
    translated = translate_dish_names(recommendations, client)
    return translated

# how to use
'''result = recommend_recipes_from_fridge('raw_menu_list.json', 'fridge_inventory.json',3)
for score, dish_id, dish_name in result:
    print(f"✅ 推荐：{dish_name}（菜谱编号：{dish_id}），优先级得分：{score:.2f}")'''
