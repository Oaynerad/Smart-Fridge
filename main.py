from smart_fridge_tracker import SmartFridgeTracker,extract_display_names,get_display_names_from_file
import os
import sys
from smart_fridge_RAG import smart_fridge_RAG
from save_raw_menu_list import save_raw_menu_list_to_json
import json
import pandas as pd
# 创建追踪器实例
def SmartFridge():
    print("Start Detecting...🤔🤔🤔")
    tracker = SmartFridgeTracker()


    result = tracker.process_fridge_update("sample_image_model_fridge/6.jpg")
    if result["success"]:
        print("冰箱内容更新成功！")
        print(f"Changes:{result['changes']}")
    else:
        print(f"更新失败:\n{result}")

    print("Start Retrieving Recipes...🥡🧐🥡🧐🥡🧐🥡🧐🥡")
    keyword = get_display_names_from_file("fridge_inventory.json")
    raw_menu_list = smart_fridge_RAG(knowledge_path='RAG/scrape',keywords = keyword)
    raw_menu_list_path = save_raw_menu_list_to_json(raw_menu_list)
    print("Start Recommending Recipes...🍴🥳🍴🥳🍴🥳🍴🥳🍴")
    from recommendation import recommend_recipes_from_fridge

    result = recommend_recipes_from_fridge('raw_menu_list.json', 'fridge_inventory.json', 3) #  推荐3道菜
    for score, dish_id, dish_name, cook_method in result:
        print(f"✅ Recommend：{dish_name}（Dish ID：{dish_id}），Score：{score:.2f}，Cook method：{cook_method}")
    
    return result

def save_recommendation_result(result, path="recommended_recipes.json"):
    data = []
    for score, dish_id, dish_name,cook_method in result:
        data.append({
            "id": dish_id,
            "name": dish_name,
            "score": score,
            "cook_method":cook_method
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} recommendations to {path}")
    
if __name__ == "__main__":
    result = SmartFridge()
    save_recommendation_result(result)