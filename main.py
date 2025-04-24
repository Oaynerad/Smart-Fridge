from smart_fridge_tracker import SmartFridgeTracker,extract_display_names,get_display_names_from_file
import os
import sys
from smart_fridge_RAG import smart_fridge_RAG

import pandas as pd
# 创建追踪器实例
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
print("Start Recommending Recipes...🍴🥳🍴🥳🍴🥳🍴🥳🍴")
from recommendation import recommend_recipes_from_fridge

result = recommend_recipes_from_fridge(raw_menu_list, 'fridge_inventory.json', dish_amount=3) #  推荐3道菜
for score, dish_id, dish_name in result:
    print(f"✅ 推荐：{dish_name}（菜谱编号：{dish_id}），优先级得分：{score:.2f}")