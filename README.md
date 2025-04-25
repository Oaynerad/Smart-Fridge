# Smart Fridge 
## Installation

1. **Clone the repo**:
   ```bash
   git clone <repository_url>
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ``` 

## Temperature from PICO
1. **run the `wifi_trans.py` on PICO**

2. **run the flask server**:
   ```bash
   python server.py
   ```
   _WIFI password and server ip needs to be modified_

3. **run UI.py**:
  ```bash
   streamlit run UI.py
   ```
## SmartFridgeTracker

A lightweight Python utility to track and manage refrigerator inventory by analyzing images using a Vision-Language Model (VLM) via the OpenAI API. It detects items, normalizes names, reconciles synonyms, and calculates freshness over time.

### Features

- **Image Encoding**: Convert local images to Base64 for API calls.
- **VLM Integration**: Use OpenAI’s `gpt-4.1-mini` to recognize food items in images.
- **Name Normalization**: Strip whitespace and lowercase names for consistent matching.
- **Synonym Reconciliation**: Detect aliases (e.g., "青苹果" vs. "绿苹果") with an LLM prompt and merge entries.
- **Inventory Management**:
  - Add new items, update `last_seen`, remove missing items.
  - Store `display_name`, `added_date`, `last_seen`, and `aliases` in a JSON DB.
- **Freshness Tracking**: Compute remaining shelf life (default 7 days) for each item.
- **Standalone CLI Usage**: Process an image and output changes.



### Configuration

- **`db_path`**: Path to the JSON inventory file (`fridge_inventory.json` by default).
- **OpenAI API Key**: Set via `OPENAI_API_KEY` environment variable.

### Usage

```bash
python smart_fridge.py 
```

This will:

1. Encode and analyze the image.
2. Parse the returned JSON for `specific_name` fields.
3. Update the local inventory (`fridge_inventory.json`).
4. Reconcile synonyms via LLM.
5. Compute and save freshness information.
6. Print added/removed items and a timestamp.

### Core Components

#### `encode_image(image_path: str) -> str`
Encodes an image to Base64 for embedding in requests.

#### `_normalize_name(name: str) -> str`
Strips whitespace and lowercases names for deduplication.

#### `SmartFridgeTracker` Class

- **`_load_inventory()` / `_save_inventory()`**: Manage JSON DB.
- **`capture_image()`**: Verify image file exists.
- **`analyze_image()`**: Call VLM to detect `specific_name` items.
- **`_reconcile_names()`**: Prompt LLM to map new names to existing aliases.
- **`update_inventory(detected_items)`**: Add/update/remove items based on detection.
- **`update_freshness(shelf_life_days)`**: Calculate remaining days.
- **`process_fridge_update(image_path)`**: End-to-end pipeline.

### JSON Extraction Utility

The helper `extract_json_from_string(text: str)` uses regex to pull a JSON array from VLM responses, supporting both fenced and inline formats.

### Example

```python
from smart_fridge_tracker import SmartFridgeTracker

tracker = SmartFridgeTracker(db_path="my_fridge.json")
result = tracker.process_fridge_update("images/fridge.jpg")
print(result)
```

Output:
```json
{
  "success": true,
  "detected_items": [{"specific_name": "青苹果"}, ...],
  "changes": {"added": ["青苹果"], "removed": []},
  "timestamp": "2025-04-23T20:00:00"
}
```

---

Feel free to customize shelf life, database path, or extend VLM prompting logic as needed.

