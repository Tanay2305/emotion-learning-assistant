# app/services/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

TOPIC_PATH = os.path.join(BASE_DIR, "shared", "topic.json")
ATTENTION_PATH = os.path.join(BASE_DIR, "shared", "attention_state.json")
CONTROL_PATH = os.path.join(BASE_DIR, "shared", "session_control.json")