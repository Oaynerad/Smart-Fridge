import streamlit as st
import json
import requests
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from main import SmartFridge

FLASK_SERVER = "http://192.168.31.173:5000"

st.title("🏠 Smart Fridge Dashboard")
st_autorefresh(interval=5_000, key="temp_refresh")

# Temperature
try:
    resp = requests.get(f"{FLASK_SERVER}/temperature", timeout=5)
    resp.raise_for_status()
    data = resp.json()
    st.metric("Fridge Temperature", f"{data.get('temp_c','--')}°C", f"{data.get('temp_f','--')}°F")
except Exception as e:
    st.error(f"无法获取温度: {e}")

# Food Details
def load_fridge_items(path="fridge_inventory.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f).get("items", {})
    return [
        {
            "name": v.get("display_name", key),
            "added_date": v["added_date"].split("T")[0],
            "freshness": v.get("freshness_remaining")
        }
        for key, v in data.items()
    ]

st.subheader("📋 Food Details")
for item in load_fridge_items():
    st.write(f"🍎 **{item['name']}** — Added: {item['added_date']} | Freshness: {item['freshness']} days remaining")

# Fridge Image
st.subheader("🖼️ Fridge Image")
st.image("sample_image_model_fridge/6.jpg", caption="Latest Image from the Fridge", use_container_width=True)

# Recipe Recommendations
st.subheader("🍲 Recipe Recommendations")
count = st.number_input("How many recipes would you like to recommend?", 1, 5, 2)

if st.button("📥 Get Recommendations"):
    with st.spinner("Running fridge analysis…"):
        keyword, raw_menu_list, scored = SmartFridge()

    # If you want the top-N from raw_menu_list (no scoring):
    # recommended = raw_menu_list[:count]

    # Or, if you want to use your scored list:
    # `scored` is [(score, dish_id, dish_name), …]
    # build a quick lookup from dish_name → details
    details_map = { r["name"]: r["details"] for r in raw_menu_list }
    recommended = []
    for score, dish_id, dish_name in scored:
        if dish_name in details_map:
            recommended.append({
                "name":  dish_name,
                "details": details_map[dish_name]
            })
        if len(recommended) >= count:
            break

    st.session_state.recommended = recommended

# Display them
if "recommended" in st.session_state:
    for recipe in st.session_state.recommended:
        with st.expander(recipe["name"]):
            st.write(recipe["details"])
