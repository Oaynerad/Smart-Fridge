# Smart Fridge 
Daren Yao | Jinsong Yuan | Jiarui Zhang

### **Tracker - RAG(recipe) - Recommender**

We designed an intelligent refrigerator system that integrates **food recognition** and freshness tracking, **generates recipe candidates** using Retrieval-Augmented Generation (RAG), and optimizes recommendations based on primary ingredients to **reduce food waste and ensure nutritional balance.**
## Installation

1. **Clone the repo**:
   ```bash
   git clone <repository_url>
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ``` 

## DEMO
Exact steps to run the whole pipeline
### I. Start obtaining Temperature from PICO
1. **run the `wifi_trans.py` on PICO**

    _WIFI password and server ip needs to be modified_
2. **run the flask server**:
   ```bash
   python server.py
   ```
   

3. **run UI.py**: (Just to check whether the temp works - the recipe is just the last recommendation based on our last run)
    ```bash
   streamlit run UI.py
   ```

### II. Obtain the photo
- run `python拉流截图.py`
- update the path for `tracker.process_fridge_update("sample_image_model_fridge/6.jpg")` in `main.SmartFridge`
### III. Let's go!
```bash
 python main.py
 streamlit run UI.py
 ```
### Demo variants
- To test the tracker, just change the food in the fridge model and rerun the whole pipeline. (I will explain the Chinese output)
- To test the recommender, we can manually change the added_date to make some food "unfresh", which will make it's score higher
## SmartFridgeTracker
_Daren Yao_

A lightweight Python utility to track and manage refrigerator inventory by analyzing images using a Vision-Language Model (VLM) via the OpenAI API. It detects items, normalizes names, reconciles synonyms, and calculates freshness over time.

In `smart_fridge_tracker.py`, I implemented a LLM pipeline in a class `SmartFridgeTracker` that could update `fridge_inventory.json` with new fridge photos.

The core function is based on two steps of calling LLM in `update_inventory`: 
- `analyze_image`: Recognize the contents of the refrigerator by VLM and generate stable output (Part of the prompt: “Be sure to keep the naming stable in the same scenario without the brand message.”)
- `_reconcile_names`: Ask the LLM to judge whether the new specific name is a new food in the fridge or just a alias. (And output the mapping dict)


### Features

- **Image Encoding**: Convert local images to Base64 for API calls.
- **VLM Integration**: Use OpenAI’s `gpt-4.1-mini` to recognize food items in images.
- **Name Normalization**: Strip whitespace and lowercase names for consistent matching.
- **Synonym Reconciliation**: Detect aliases (e.g., "purple eggplant" vs "eggplant") with an LLM prompt and merge entries.
- **Inventory Management**:
  - Add new items, update `last_seen`, remove missing items.
  - Store `display_name`, `added_date`, `last_seen`, and `aliases` in a JSON DB.
- **Freshness Tracking**: Compute remaining shelf life (default 7 days) for each item.



### Configuration

- **`db_path`**: Path to the JSON inventory file (`fridge_inventory.json` by default, we will use this name for the whole project).
- **OpenAI API Key**: Set via `OPENAI_API_KEY` environment variable.


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





