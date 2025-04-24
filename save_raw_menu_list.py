def save_raw_menu_list_to_json(raw_menu_list, filename="raw_menu_list.json"):
    import json
    import os

    # 清洗并解析列表
    cleaned_list = []
    for item in raw_menu_list:
        if item == 'None' or item is None:
            cleaned_list.append(None)
        else:
            try:
                parsed = json.loads(item)
                cleaned_list.append(parsed)
            except Exception:
                cleaned_list.append(item)  # 保留原始格式（不推荐）

    # 设置路径
    output_path = os.path.join(filename)

    # 写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_list, f, ensure_ascii=False, indent=4)

    return output_path
