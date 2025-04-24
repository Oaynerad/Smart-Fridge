import streamlit as st
from datetime import datetime

# 初始化状态
if "page" not in st.session_state:
    st.session_state.page = "首页"
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None

def go_to(page):
    st.session_state.page = page

# 示例数据
fridge_items = [
    {"name": "鸡蛋", "added_date": "2025-04-21"},
    {"name": "生菜", "added_date": "2025-04-23"},
    {"name": "猪肉", "added_date": "2025-04-22"},
]

recipe_list = [
    {"name": "番茄炒蛋", "id": 1, "details": "做法：番茄炒蛋……"},
    {"name": "蒜蓉生菜", "id": 2, "details": "做法：蒜蓉炒生菜……"},
    {"name": "红烧肉", "id": 3, "details": "做法：红烧肉……"},
]

# 主页面 - 首页
if st.session_state.page == "首页":
    st.title("🏠 智能冰箱首页")

    # 温度显示区域
    st.header("🌡️ 当前温度")
    st.metric("冰箱温度", "4°C", "-0.5°C")
    if st.button("切换为 ℉"):
        st.success("切换为华氏度功能尚未实现")

    # 食品存放区域
    st.header("🧊 冰箱内食品存放")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 食品详细情况"):
            go_to("食品详细")
    with col2:
        if st.button("🖼️ 图片显示"):
            go_to("图片展示")

    # 菜谱推荐按钮
    st.header("🍲 菜谱推荐")
    if st.button("🔍 进入菜谱推荐"):
        go_to("菜谱推荐")

# 食品详细页面
elif st.session_state.page == "食品详细":
    st.title("📋 食品详细信息")
    for item in fridge_items:
        st.write(f"食材：{item['name']}，入库时间：{item['added_date']}")
    st.button("🔙 返回", on_click=lambda: go_to("首页"))

# 图片展示页面
elif st.session_state.page == "图片展示":
    st.title("🖼️ 冰箱内图片展示")
    st.image("https://placekitten.com/400/300", caption="冰箱内拍摄图像")
    st.button("🔙 返回", on_click=lambda: go_to("首页"))

# 菜谱推荐主页面
elif st.session_state.page == "菜谱推荐":
    st.title("🍽️ 菜谱推荐")
    count = st.number_input("你想要推荐几道菜？", min_value=1, max_value=5, value=2, step=1)
    if st.button("📥 获取推荐结果"):
        st.session_state.recommended = recipe_list[:count]

    # 展示推荐结果
    if "recommended" in st.session_state:
        for recipe in st.session_state.recommended:
            with st.expander(recipe["name"]):
                if st.button(f"🔍 查看 {recipe['name']} 详情", key=f"view_{recipe['id']}"):
                    st.session_state.selected_recipe = recipe
                    go_to("菜谱详情")

    st.button("🔙 返回首页", on_click=lambda: go_to("首页"))

# 菜谱详细信息页面
elif st.session_state.page == "菜谱详情":
    recipe = st.session_state.selected_recipe
    st.title(f"🍛 {recipe['name']} 的详细信息")
    st.write(recipe["details"])
    st.button("🔙 返回菜谱推荐", on_click=lambda: go_to("菜谱推荐"))

# streamlit run "D:\CMU\12770\Fridge\Smart-Fridge\UI.py"