from smart_fridge_tracker import SmartFridgeTracker,extract_display_names,get_display_names_from_file
import os
import sys
from smart_fridge_RAG import smart_fridge_RAG
from recommendation import recommend_recipes_from_fridge
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

print("Start Retrieving Recipes...🥡    🥡    🥡")
keyword = get_display_names_from_file("fridge_inventory.json")
raw_menu_list = smart_fridge_RAG(knowledge_path='RAG/scrape',keywords = keyword)

print("Start Recommending Recipes...🍴 🍴 🍴")
# 调用示例
# 原始字符串列表（示例数据）
# raw_menu_list = ['```json\n[\n    {\n        "菜谱编号": 663731,\n        "菜名": "肉沫泡紫茄",\n        "卡路里": "600大卡",\n        "碳足迹": "0.4 千克二氧化碳当量",\n        "食材": [\n            "猪肉（200g）",\n            "紫皮茄子（2个）",\n            "姜（3片）",\n            "青辣椒（1个）",\n            "豆瓣酱（1勺）",\n            "耗油（1匙）",\n            "酱油（半匙）",\n            "花生油（2勺）",\n            "盐（半匙适量）",\n            "小米辣椒（1个）",\n            "洋葱（3块）",\n            "清水（5勺）"\n        ],\n        "蛋白质": "30g",\n        "脂肪": "40g",\n        "碳水化合物": "20g",\n        "纤维 素": "10g"\n    },\n    {\n        "菜谱编号": 663572,\n        "菜名": "酸菜炖粉条",\n        "卡路里": "500大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        "食材": [\n            "东北酸菜（400g）",\n            "猪肉（1块）",\n            "粉条（适量）",\n            "生抽（1匙）",\n            "葱姜片（少许）"\n        ],\n        "蛋白质": "25g",\n        "脂肪": "20g",\n        "碳水化合物": "60g",\n        "纤维素": "15g"\n    },\n    {\n        "菜谱编号": 663486,\n        "菜名": "大肚虾仁馄饨独家",\n        "卡路里": "700大卡",\n        "碳足迹": "0.6 千克二氧化碳当量",\n        "食材": [\n            "虾仁（8个）",\n            "猪肉馅（适量）",\n            "胡萝卜（1节）",\n            "食用油（1勺）",\n            "馄饨皮（适量）",\n            "盐（少许）",\n           "生抽（少许）"\n        ],\n        "蛋白质": "35g",\n        "脂肪": "30g",\n        "碳水化合物": "50g",\n        "纤维素": "5g"\n    }\n]\n```', '```json\n[\n    {\n        "菜谱编号": 663719,\n        "菜名": "低脂低卡银芽牛肉拌饭",\n        "卡路里": "350大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        " 食材": [\n            "绿豆芽（200g）",\n            "胡萝卜（1块）",\n            "牛肉沫（80g）",\n            "大米饭（100g）",\n            "小葱（1颗）",\n            "盐（1g）",\n            "白胡椒粉（1g）",\n            "生抽（1勺）",\n            "淀粉（拌肉）（0.25勺）",\n            "老抽（0.25勺）"\n        ],\n        "蛋白质": "25g",\n        "脂肪": "10g",\n        "碳水化合物": "50g",\n        "纤维素": "5g"\n    },\n    {\n        "菜谱编号": 663558,\n        " 菜名": "红焖牛肉",\n        "卡路里": "600大卡",\n        "碳足迹": "0.6 千克二氧化碳当量",\n        "食材": [\n            "牛肉（适量）",\n            "大葱段 （适量）",\n            "大料（1个）",\n            "花椒粉（适量）",\n            "香叶（2片）",\n            "白芷（2片）",\n            "桂皮（少许）",\n            "桅子（2个（上色作用））",\n            "干红椒（2个）",\n            "盐（适量）",\n            "生抽（适量）",\n            "红烧酱油（适量）",\n            "糖（1勺）",\n            "腐乳汁（适量）"\n        ],\n        "蛋白质": "40g",\n        "脂肪": "30g",\n        "碳水化合物": "20g",\n        "纤维素": "3g"\n    }\n]\n```', '```json\n[\n    {\n        "菜谱编号": 663062,\n        "菜名": "葱爆羊肉卷独家",\n        "卡路里": "600大卡",\n        "碳足迹": "0.4 千克二氧化碳当量",\n        "食材": [\n            "羊肉卷（适量）",\n            "大葱（适量）",\n            "香菜（适量）",\n            "胡椒粉（适量）",\n            "芝麻（适量）",\n            "姜（适量）",\n            "生抽（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "30g",\n        "脂肪": "20g",\n        "碳水化合物": "10g",\n        "纤维素": "2g"\n    },\n    {\n        "菜谱编号": 662950,\n        "菜名": "青萝卜全羊汤独家",\n        "卡路里": "500大卡",\n        "碳足迹": "0.3 千克二氧化碳当量",\n        "食材": [\n            "羊肉（适量）",\n            "羊杂（适量）",\n            "青萝卜（适量）",\n            "胡椒粉（适量）",\n            "水（适量）",\n            "姜（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "25g",\n        "脂 肪": "15g",\n        "碳水化合物": "15g",\n        "纤维素": "3g"\n    },\n    {\n        "菜谱编号": 662888,\n        "菜名": "羊肉水煎饺独家",\n        "卡路里": "700大卡",\n        "碳足迹": "0.5 千克二氧化碳当量",\n        "食材": [\n            "羊肉（适量）",\n            "面粉（适量）",\n            "香菜（适量）",\n            "胡萝卜（适量）",\n            "生抽（适量）",\n            "老抽（适量）",\n            "胡椒粉（适量）",\n            "五香粉（适量）",\n            "姜（适量）",\n            "盐（适量）"\n        ],\n        "蛋白质": "35g",\n        "脂肪": "25g",\n        "碳水化合物": "80g",\n        "纤维素": "4g"\n    }\n]\n```']
result = recommend_recipes_from_fridge(raw_menu_list, 'fridge_inventory.json', dish_amount=3) #  推荐3道菜
for score, dish_id, dish_name in result:
    print(f"✅ 推荐：{dish_name}（菜谱编号：{dish_id}），优先级得分：{score:.2f}")