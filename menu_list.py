# 用于从json提取标准的数据，包括冰箱库存和菜谱信息

import json
import pandas as pd
import re


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

        for ing in recipe.get("主料", []):
            # print(f"食材：{ing}")
            ingredient_rows.append({
                "菜谱编号": recipe_id,
                "菜名": name,
                "主料": ing.strip()
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

    ingredient_df["原始食材"] = ingredient_df["主料"]
    ingredient_df[["主料", "量"]] = ingredient_df["原始食材"].apply(lambda x: pd.Series(split_ingredient(x)))
    ingredient_df.drop(columns=["原始食材"], inplace=True)

    grouped = ingredient_df.groupby(['菜谱编号', '菜名'])['主料'].apply(list).reset_index()
    ing_df = grouped['主料'].apply(pd.Series)
    final_df = pd.concat([grouped[['菜谱编号', '菜名']], ing_df], axis=1)
    ingredient_columns = final_df.columns[2:]
    final_df["食材列表"] = final_df[ingredient_columns].apply(lambda row: row.dropna().tolist(), axis=1) 
    
    return main_info_df, final_df

# print("\n--- 主营养信息表 ---")
# print(main_df)

'''print("\n--- 食材明细表（拆分） ---")
print(ing_df)'''

# 获取冰箱库存和新鲜度信息函数
def get_fridge_inventory(json_file_path):
    # 读取 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 提取食材及其 freshness_remaining
    items = data['items']
    records = [
        {"主料": name, "保鲜剩余天数": info.get("freshness_remaining", None)}
        for name, info in items.items()
    ]
    # 转为 DataFrame
    fridge_ingredients = pd.DataFrame(records)
    return fridge_ingredients

'''fridge_ingredients=get_fridge_inventory('fridge_inventory.json')
print(fridge_ingredients)'''
