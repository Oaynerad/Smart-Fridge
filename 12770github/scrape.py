import os
import requests
from bs4 import BeautifulSoup
import time
import re
headers = {
    "User-Agent": "Mozilla/5.0"
}

# 创建保存目录
os.makedirs("scrape", exist_ok=True)

# 打开输出文件（如果存在则覆盖）
with open("scrape/recipes.txt", "a", encoding="utf-8") as output_file:

    for recipe_id in range(663572, 660000, -1):
        url = f"https://home.meishichina.com/recipe-{recipe_id}.html"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, "html.parser")

            # 菜名
            title_tag = soup.find("h1", class_="recipe_De_title")
            if not title_tag:
                print(f"⚠️ 页面结构异常，跳过：{recipe_id}")
                continue
            title = title_tag.get_text(strip=True)
            if not title:
                print(f"⚠️ 空标题，跳过：{recipe_id}")
                continue

            # 食材
            ingredients = []
            for fieldset in soup.find_all("fieldset", class_="particulars"):
                section = fieldset.find("legend").get_text(strip=True)
                for li in fieldset.select("li"):
                    name_tag = li.select_one(".category_s1")
                    amount_tag = li.select_one(".category_s2")
                    if not name_tag or not amount_tag:
                        continue
                    name = name_tag.get_text(strip=True)
                    amount = amount_tag.get_text(strip=True)
                    ingredients.append(f"{section}：{name}（{amount}）")
            if not ingredients:
                print(f"⚠️ 无食材，跳过：{recipe_id}")
                continue

            # 做法
            steps = []
            for step_div in soup.select(".recipeStep_word"):
                step_text = step_div.get_text(strip=True)
                if step_text:
                    steps.append(step_text)
            if not steps:
                print(f"⚠️ 无步骤，跳过：{recipe_id}")
                continue

            # 拼接食材
            ingredient_str = "、".join(ingredients)

            steps_str = "、".join([
                re.sub(r"[。．.、]+$", "", step.lstrip("0123456789.、:： ").strip())
                for step in steps
            ])

            #    拼成自然语言段落
            text_block = (
                f"菜谱编号：{recipe_id}，菜名：{title}。"
                f"食材包括：{ingredient_str}。"
                f"做法步骤如下：{steps_str}。\n\n"
            )

            # 写入文件
            output_file.write(text_block)




            print(f"✅ 已抓取：{recipe_id} - {title}")
            time.sleep(0.5)

        except Exception as e:
            print(f"⚠️ 异常跳过 {recipe_id}: {e}")
