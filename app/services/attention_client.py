import json
import os
from app.services.config import ATTENTION_PATH

def get_attention():
    if not os.path.exists(ATTENTION_PATH):
        return "Unknown", 0

    with open(ATTENTION_PATH) as f:
        data = json.load(f)

    return data.get("attention", "Unknown"), data.get("timestamp", 0)