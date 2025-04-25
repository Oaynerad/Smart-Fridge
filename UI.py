import streamlit as st
import json
from datetime import datetime
import time
import requests
from streamlit_autorefresh import st_autorefresh
from main import SmartFridge



# --- load fridge inventory from JSON ---
def load_fridge_items(path="fridge_inventory.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f).get("items", {})
    items = []
    for key, v in data.items():
        # parse out just the date, and freshness
        added = v.get("added_date", "").split("T")[0]
        freshness = v.get("freshness_remaining", None)
        items.append({
            "name": v.get("display_name", key),
            "added_date": added,
            "freshness": freshness
        })
    return items

# --- load recipe recommendation from JSON ---
def get_recommendations(path="recommended_recipes.json"):
    import json
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 可以增加更多字段（如详情）作为 st.write 的内容
    for item in data:
        item["details"] = f"Score: {item['score']:.2f} (Dish ID: {item['id']})"
    return data



FLASK_SERVER = "http://192.168.31.173:5000"  # 比如 http://192.168.31.104

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None

st.title("🏠 Smart Fridge Dashboard")
st_autorefresh(interval=5_000, key="temp_refresh")

# 温度展示
try:
    resp = requests.get(f"{FLASK_SERVER}/temperature", timeout=5)
    resp.raise_for_status()
    data = resp.json()
    temp_c = data.get("temp_c", "--")
    temp_f = data.get("temp_f", "--")
    st.metric("Fridge Temperature", f"{temp_c}°C", f"{temp_f}°F")
except Exception as e:
    st.error(f"无法获取温度: {e}")

# 食物信息
st.subheader("📋 Food Details")
fridge_items = load_fridge_items()
for item in fridge_items:
    st.write(f"🍎 **{item['name']}** — Added: {item['added_date']} | Freshness: {item['freshness']} days remaining")

# 图片展示
st.subheader("🖼️ Fridge Image")
st.image("sample_image_model_fridge/6.jpg", caption="Latest Image from the Fridge", use_container_width=True)

# 推荐系统
st.subheader("🍲 Recipe Recommendations")
count = st.number_input("How many recipes would you like to recommend?", min_value=1, max_value=5, value=2, step=1)

if st.button("📥 Get Recommendations"):
    st.session_state.recommended = get_recommendations()[:count]

if "recommended" in st.session_state:
    for recipe in st.session_state.recommended:
        with st.expander(recipe["name"]):
            st.write(recipe["details"])


# streamlit run UI.py