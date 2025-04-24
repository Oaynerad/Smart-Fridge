import os
import json
import datetime
import base64
import re
from typing import List, Dict, Any

from PIL import Image  # 预留：未来可能用到图像处理
from openai import OpenAI

# -------------------------------------------------
# 工具函数
# -------------------------------------------------

def encode_image(image_path: str) -> str:
    """将图像编码为 base64 供 VLM 调用"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _normalize_name(name: str) -> str:
    """统一化食物名称用于去重与匹配（小写、去除空格）

    >>> _normalize_name(" 青 苹果 ")
    '青苹果'
    """
    return re.sub(r"\s+", "", name.strip().lower())


# -------------------------------------------------
# 智能冰箱追踪核心类
# -------------------------------------------------

class SmartFridgeTracker:
    """智能冰箱内容追踪系统——仅依赖 specific_name 字段"""

    def __init__(self, db_path: str = "fridge_inventory.json") -> None:
        self.db_path = db_path
        self.inventory = self._load_inventory()
        # 结构示例：
        # {
        #   "items": {
        #       "青苹果": {
        #           "display_name": "青苹果",
        #           "added_date": "2025-04-22T13:00:00",
        #           "last_seen": "2025-04-22T13:00:00",
        #           "freshness_remaining": 7,
        #           "aliases": []
        #       }
        #   },
        #   "last_updated": "...",
        #   "freshness_last_updated": "..."
        # }

    # ---------- 本地数据库读写 ----------

    def _load_inventory(self) -> Dict[str, Any]:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("数据库文件损坏，重新创建")
        else:
            print("数据库文件不存在，创建新的库存数据")
        return {"items": {}, "last_updated": None}

    def _save_inventory(self) -> None:
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.inventory, f, ensure_ascii=False, indent=2)

    # ---------- 图像采集 ----------

    def capture_image(self, image_path: str) -> bool:
        if os.path.exists(image_path):
            print(f"使用现有图像: {image_path}")
            return True
        print(f"错误: 图像不存在: {image_path}")
        return False

    # ---------- VLM 调用 ----------

    def analyze_image(self, image_path: str) -> str:
        """调用 VLM 识别冰箱中的食物，返回 JSON 字符串"""
        client = OpenAI()
        base64_image = encode_image(image_path)
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "请根据提供的冰箱内部照片识别图片中的食物，并生成 JSON 数组。"
                                "每个对象仅包含一个字段 specific_name。"
                                "务必在同样的场景下保持命名稳定，不包含品牌信息。"
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content

    # ---------- 名称对齐（同名 / 别名 合并） ----------

    def _reconcile_names(self, prev_names: List[str], curr_names: List[str]) -> Dict[str, str]:
        """使用 LLM 判断当前检测到的名称是否为已有名称的同义词

        返回字典 mapping[current_norm_name] = prev_norm_name
        如果认为是新增，则不在映射表中
        """
        if not prev_names:
            return {}

        client = OpenAI()
        prompt = f"""已知冰箱中已有以下食物名称列表：
            {', '.join(prev_names)}
            现在检测到新的名称列表：
            {', '.join(curr_names)}
            请判断哪些新名称与已有名称代表同一种食物，输出 JSON 数组，每个对象格式：{{
            \"new\": \"(新名称)\",
            \"existing\": \"(匹配的旧名称)\"
            }}
            如果新名称确实是新的食物，请不要输出该名称。"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        # 解析
        try:
            mapping_raw = extract_json_from_string(response.choices[0].message.content)
            mapping = {
                _normalize_name(m["new"]): _normalize_name(m["existing"])
                for m in mapping_raw
            }
            return mapping
        except Exception as e:
            print("名称对齐失败，按完全新增处理", e)
            return {}

    # ---------- 库存更新 ----------

    def update_inventory(self, detected_items: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """根据 detected_items 更新库存，仅使用 specific_name 字段"""
        now_iso = datetime.datetime.now().isoformat()

        prev_norm_names = set(self.inventory["items"].keys())
        curr_norm_names = {_normalize_name(it["specific_name"]) for it in detected_items}

        print("\n[上一轮规范名]", prev_norm_names)
        print("[本轮规范名]", curr_norm_names)

        synonym_map = self._reconcile_names(list(prev_norm_names), list(curr_norm_names))
        merged_curr_norm_names = {synonym_map.get(n, n) for n in curr_norm_names}

        added = merged_curr_norm_names - prev_norm_names
        removed = prev_norm_names - merged_curr_norm_names
        print('[映射表]', synonym_map)
        print("[映射后规范名]", merged_curr_norm_names)
        print("[新增]", added)
        print("[移除]", removed)

        for norm_name in added:
            display_name = next(
                (it["specific_name"] for it in detected_items if _normalize_name(it["specific_name"]) == norm_name),
                norm_name,
            )
            self.inventory["items"][norm_name] = {
                "display_name": display_name,
                "added_date": now_iso,
                "last_seen": now_iso,
                "aliases": [],
            }

        for new_norm, existing_norm in synonym_map.items():
            if existing_norm in self.inventory["items"]:
                self.inventory["items"][existing_norm]["last_seen"] = now_iso
                aliases = self.inventory["items"][existing_norm].setdefault("aliases", [])
                if new_norm not in aliases:
                    aliases.append(new_norm)

        for norm_name in merged_curr_norm_names & prev_norm_names:
            self.inventory["items"][norm_name]["last_seen"] = now_iso

        for norm_name in removed:
            self.inventory["items"].pop(norm_name, None)

        self.inventory["last_updated"] = now_iso
        self._save_inventory()

        to_display = lambda s: [self.inventory["items"].get(n, {}).get("display_name", n) for n in s if n in self.inventory["items"]]
        return {"added": to_display(added), "removed": list(removed)}

    # ---------- 新鲜度计算 ----------

    def update_freshness(self, shelf_life_days: int = 7) -> None:
        now = datetime.datetime.now()
        for details in self.inventory["items"].values():
            added_date = datetime.datetime.fromisoformat(details["added_date"])
            remaining = max(shelf_life_days - (now - added_date).days, 0)
            details["freshness_remaining"] = remaining
        self.inventory["freshness_last_updated"] = now.isoformat()
        self._save_inventory()

    # ---------- 主流程 ----------

    def process_fridge_update(self, image_path: str) -> Dict[str, Any]:
        if not self.capture_image(image_path):
            return {"success": False, "error": "获取图像失败"}

        raw_output = self.analyze_image(image_path)
        try:
            detected_items = extract_json_from_string(raw_output)
        except Exception as e:
            return {"success": False, "error": f"解析 VLM 输出失败: {e}"}
        if not detected_items:
            return {"success": False, "error": "未检测到任何食物"}

        changes = self.update_inventory(detected_items)
        self.update_freshness()

        return {
            "success": True,
            "detected_items": detected_items,
            "changes": changes,
            "timestamp": datetime.datetime.now().isoformat(),
        }


# -------------------------------------------------
# JSON 提取工具
# -------------------------------------------------

def extract_json_from_string(text: str):
    """ 
    从包含 JSON 数组的字符串中提取并解析该数组。
    支持包含在 ```json ... ``` 区块或直接的 [... ] 结构。
    """
    # 匹配 ```json ... ``` 区块
    fenced_match = re.search(r'```json\s*(\[\s*[\s\S]*?\s*\])\s*```', text, re.DOTALL)
    if fenced_match:
        json_str = fenced_match.group(1)
    else:
        # 退而求其次，匹配第一个 JSON 数组
        array_match = re.search(r'(\[\s*[\s\S]*?\s*\])', text, re.DOTALL)
        if not array_match:
            raise ValueError("文本中未找到 JSON 数组。")
        json_str = array_match.group(1)
    
    return json.loads(json_str)


def extract_display_names(data: Dict[str, Any]) -> List[str]:
    """
    Extract all display_name values from the fridge-inventory JSON.

    Args:
        data: Dict loaded from JSON, with structure:
            {
              "items": {
                "<id>": { "display_name": "...", ... },
                ...
              },
              ...
            }

    Returns:
        A list of display_name strings.
    """
    return [
        item.get("display_name")
        for item in data.get("items", {}).values()
        if "display_name" in item
    ]

# If you want to load directly from a file:
def get_display_names_from_file(filepath: str) -> List[str]:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return extract_display_names(data)
# 示例用法
if __name__ == "__main__":
    # 创建追踪器实例
    tracker = SmartFridgeTracker()

    result = tracker.process_fridge_update("sample_image_model_fridge/6.jpg")
    
    # # 输出结果
    if result["success"]:
        print("冰箱内容更新成功！")
        print(f"Changes:{result['changes']}")
    else:
        print(f"更新失败:\n{result}")
