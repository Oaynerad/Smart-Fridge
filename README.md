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

3. **Python version**:
   We sugest using python 3.11.11.

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
## RAG
_Jinsong Yuan_

## Recommender
_Jiarui Zhang_

The main job of the Recommender part can be divided into 2 parts:

### ingredient_match.py 

Process JSON files containing information about the current items in the fridge and the recipes organized based on the available ingredients, and extract the relevant information. Match the main ingredients of each recipe with the available items in the fridge to obtain their freshness levels and to determine which ingredients are needed for cooking.

#### File Structure

fridge_inventory.json: Current fridge inventory, including ingredient names and remaining freshness days
raw_menu_list.json: A list of recipes, each containing main ingredients, nutritional info, etc.

#### Usage

```python
df = process_fridge_recipes('fridge_inventory.json', 'raw_menu_list.json')
```

### recommendation.py

Prioritize the use of ingredients that are close to expiring, while referring to the nutritional content and carbon footprint data of each dish. Optimize with the goals of minimizing food waste and carbon emissions, and maximizing health. Based on the number of dishes the user wishes to prepare for the day, return recipe recommendations along with their cooking methods. Additionally, since this project primarily focuses on Chinese cuisine, the established knowledge base is in Chinese. Therefore, the recommended recipes and cooking methods will be translated into English before being presented to the user.

#### function explaination

- **`parse_carbon_footprint(carbon_str)`**:	Extracts the numeric value from strings like "0.2 千克二氧化碳当量" and converts it to a float
- **`safe_float_gram(s)`**:	Converts strings like "5g" into float values
- **`force_parse_to_list(x)`**:	Safely parses a string or list into a Python list, handling cases with None or malformed input
- **`recommend_top_n_meals(final_df, fridge_df, top_n=3)`**:	Scores and ranks recipes based on ingredient match, freshness, nutrition, and carbon footprint, and returns the top n recommendations
- **`translate_dish_names(results, client)`**:	Uses GPT to translate dish names and cooking methods from Chinese to English
- **`recommend_recipes_from_fridge(raw_menu_path, fridge_inventory_path, dish_amount)`**:	Main orchestration function that loads data, matches ingredients, ranks recipes, translates results, and returns the top recommended dishes (with English translations)

#### Usage

```python
result = recommend_recipes_from_fridge('raw_menu_list.json', 'fridge_inventory.json', dish_amount)
```

## Smart Fridge Dashboard (Streamlit Interface)
_Daren Yao_, _Jiarui Zhang_


This script creates a **Streamlit-based web dashboard** for a smart fridge system, integrating real-time display, inventory status, and recipe recommendation.

### Features

| Module                     | Description                                                                    |
|----------------------------|--------------------------------------------------------------------------------|
| **Temperature Display**    | Fetches current fridge temperature from a Flask server and shows °C and °F     |
| **Fridge Inventory**       | Loads current ingredients from `fridge_inventory.json` and shows freshness     |
| **Fridge Image**           | Displays a snapshot of the fridge interior (`6.jpg` as a sample image)         |
| **Recipe Recommendations** | On button click, loads top recommended recipes from `recommended_recipes.json` |
| **Auto Refresh**           | Automatically refreshes the dashboard every 5 seconds                          |

### File Structure

- `fridge_inventory.json`: Stores fridge items and freshness days
- `recommended_recipes.json`: Contains precomputed recipe recommendations
- `sample_image_model_fridge/6.jpg`: Sample fridge interior image (can be updated live)

###  How to Run

Make sure all dependencies are installed, then run:
```bash
streamlit run UI.py
```