import streamlit as st
import json
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from smart_fridge_tracker import SmartFridgeTracker, get_display_names_from_file
from smart_fridge_RAG import smart_fridge_RAG
from save_raw_menu_list import save_raw_menu_list_to_json
from recommendation import recommend_recipes_from_fridge

# --- Helper to load fridge inventory ---
def load_fridge_items(path="fridge_inventory.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f).get("items", {})
    items = []
    for key, v in data.items():
        added = v.get("added_date", "").split("T")[0]
        freshness = v.get("freshness_remaining", None)
        items.append({
            "name": v.get("display_name", key),
            "added_date": added,
            "freshness": freshness
        })
    return items

# Initialize
tracker = SmartFridgeTracker()
st.title("🏠 Smart Fridge Dashboard")
st_autorefresh(interval=5_000, key="temp_refresh")

# --- Temperature ---
FLASK_SERVER = "http://192.168.31.173:5000"
try:
    resp = requests.get(f"{FLASK_SERVER}/temperature", timeout=5)
    resp.raise_for_status()
    data = resp.json()
    temp_c = data.get("temp_c", "--")
    temp_f = data.get("temp_f", "--")
    st.metric("Fridge Temperature", f"{temp_c}°C", f"{temp_f}°F")
except Exception as e:
    st.error(f"无法获取温度: {e}")

# --- Food Details ---
st.subheader("📋 Food Details")
for item in load_fridge_items():
    st.write(f"🍎 **{item['name']}** — Added: {item['added_date']} | Freshness: {item['freshness']} days remaining")

# --- Fridge Image ---
st.subheader("🖼️ Fridge Image")
st.image("sample_image_model_fridge/6.jpg", caption="Latest Image from the Fridge", use_container_width=True)

# --- Recipe Recommendations ---
st.subheader("🍲 Recipe Recommendations")
count = st.number_input("How many recipes would you like to recommend?", min_value=1, max_value=5, value=2, step=1)
if st.button("📥 Update & Get Recommendations"):
    with st.spinner("Processing fridge data and fetching recipes..."):
        # Update inventory
        result = tracker.process_fridge_update("sample_image_model_fridge/6.jpg")
        if not result.get("success", False):
            st.error(f"更新失败: {result}")
        else:
            st.success("冰箱内容更新成功！")
            st.write(f"Changes: {result['changes']}")
        # Retrieve recipes via RAG
        keywords = get_display_names_from_file("fridge_inventory.json")
        raw_menu_list = smart_fridge_RAG(knowledge_path='RAG/scrape', keywords=keywords)
        raw_menu_list_path = save_raw_menu_list_to_json(raw_menu_list)
        # Generate recommendations
        recs = recommend_recipes_from_fridge(raw_menu_list_path, "fridge_inventory.json", count)
        # Build display list
        try:
            with open(raw_menu_list_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
        except Exception:
            raw_data = []
        display_recs = []
        for score, dish_id, dish_name in recs:
            # find details
            item = next((r for r in raw_data if r.get('id') == dish_id), {})
            display_recs.append({"name": dish_name, "details": item})
        st.session_state.recommended = display_recs

# Show recommendations
if "recommended" in st.session_state:
    for recipe in st.session_state.recommended:
        with st.expander(recipe["name"]):
            st.json(recipe["details"])
