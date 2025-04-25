import streamlit as st
import json
from datetime import datetime
import time
import requests
from streamlit_autorefresh import st_autorefresh

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



FLASK_SERVER = "http://192.168.31.173:5000"  # 比如 http://192.168.31.104

if "page" not in st.session_state:
    st.session_state.page = "Home"
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None

def go_to(page):
    st.session_state.page = page

if st.session_state.page == "Home":
    st.title("🏠 Smart Fridge Home")

    # 自动刷新 every 5s
    st_autorefresh(interval=5_000, key="temp_refresh")

    try:
        resp = requests.get(f"{FLASK_SERVER}/temperature", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        temp_c = data.get("temp_c", "--")
        temp_f = data.get("temp_f", "--")
        st.metric("Fridge Temperature", f"{temp_c}°C", f"{temp_f}°F")
    except Exception as e:
        st.error(f"无法获取温度: {e}")


    # —— 下面是你原有的按钮导航 —— 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Food Details"):
            go_to("Food Details")
    with col2:
        if st.button("🖼️ Image Display"):
            go_to("Image Display")

    st.header("🍲 Recipe Recommendations")
    if st.button("🔍 Go to Recipe Recommendations"):
        go_to("Recipe Recommendations")

 
# Food details page
elif st.session_state.page == "Food Details":
    fridge_items = load_fridge_items()
    st.title("📋 Food Details")
    for item in fridge_items:
        st.write(f"Item: {item['name']}, Added Date: {item['added_date']}")
    st.button("🔙 Back", on_click=lambda: go_to("Home"))

# Image display page
elif st.session_state.page == "Image Display":
    st.title("🖼️ Fridge Image Display") 
    st.image("https://placekitten.com/400/300", caption="Image taken inside the fridge")
    st.button("🔙 Back", on_click=lambda: go_to("Home"))

# Recipe recommendations main page
elif st.session_state.page == "Recipe Recommendations":
    st.title("🍽️ Recipe Recommendations")
    count = st.number_input("How many recipes would you like to recommend?", min_value=1, max_value=5, value=2, step=1)
    if st.button("📥 Get Recommendations"):
        st.session_state.recommended = recipe_list[:count]

    # Display recommended recipes
    if "recommended" in st.session_state:
        for recipe in st.session_state.recommended:
            with st.expander(recipe["name"]):
                if st.button(f"🔍 View {recipe['name']} Details", key=f"view_{recipe['id']}"):
                    st.session_state.selected_recipe = recipe
                    go_to("Recipe Details")

    st.button("🔙 Back to Home", on_click=lambda: go_to("Home"))

# Recipe details page
elif st.session_state.page == "Recipe Details":
    recipe = st.session_state.selected_recipe
    st.title(f"🍛 {recipe['name']} Details")
    st.write(recipe["details"])
    st.button("🔙 Back to Recipe Recommendations", on_click=lambda: go_to("Recipe Recommendations"))

# streamlit run UI.py