# 初版优化算法，待调整

import pandas as pd
from datetime import datetime, timedelta

def compute_freshness_score(ingredient_name, fridge_df, today):
    """根据食材入库时间计算新鲜度评分：越接近过期分值越低"""
    rows = fridge_df[fridge_df['食材'] == ingredient_name]
    if rows.empty:
        return float('inf')  # 不存在该食材
    days_left = [(7 - (today - row['入库时间']).days) for _, row in rows.iterrows()]
    # 越小越优先，0快过期，负值已过期
    return min([max(0, d) for d in days_left])

def recommend_meals(main_info_df, ingredient_df, fridge_df, days=3):
    from datetime import datetime, timedelta

    today = datetime.today()
    recommendations = []
    used_dish_ids = set()

    def none_to_0g(val):
        """如果为 None，则返回 '0g'；否则保持原样"""
        if val is None or str(val).lower() == 'none':
            return "0g"
        return str(val)

    def safe_float_gram(val):
        """从形如 '30g' 的字符串中提取数值部分为 float"""
        return float(none_to_0g(val).replace("g", "").strip())

    for t in range(days):
        best_score = float('inf')
        best_dish = None

        for idx, row in main_info_df.iterrows():
            dish_id = row['菜谱编号']
            dish_name = row['菜名']
            if dish_id in used_dish_ids:
                continue  # 避免重复推荐

            try:
                carbon = float(str(row.get('碳足迹', '0')).split()[0])
            except:
                carbon = 0.0

            # 将 None → '0g' 再提取数值
            protein = safe_float_gram(row.get('蛋白质'))
            fat = safe_float_gram(row.get('脂肪'))
            carb = safe_float_gram(row.get('碳水化合物'))
            fiber = safe_float_gram(row.get('纤维素', row.get('纤维 素')))

            ingredients = ingredient_df[ingredient_df['菜谱编号'] == dish_id]
            freshness_score = 0
            feasible = True

            for _, ing in ingredients.iterrows():
                ing_name = ing['食材']
                if compute_freshness_score(ing_name, fridge_df, today) == float('inf'):
                    feasible = False
                    break
                freshness_score += compute_freshness_score(ing_name, fridge_df, today)

            if not feasible:
                continue

            score = 0.7 * freshness_score + 0.3 * carbon

            if score < best_score:
                best_score = score
                best_dish = (dish_id, dish_name)

        if best_dish:
            recommendations.append(best_dish)
            used_dish_ids.add(best_dish[0])

            # 可选：移除使用过的食材
            used_ingredients = ingredient_df[ingredient_df['菜谱编号'] == best_dish[0]]
            for _, ing in used_ingredients.iterrows():
                fridge_df = fridge_df[fridge_df['食材'] != ing['食材']]
        else:
            print(f"⚠️ 第 {t+1} 天：找不到可行的菜品，跳过。")
        today += timedelta(days=1)
        

    return recommendations

