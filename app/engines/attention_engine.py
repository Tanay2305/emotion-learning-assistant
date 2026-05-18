import cv2
import time
import json
import os
import numpy as np
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from pathlib import Path


# ---------------- PATHS ----------------
BASE_DIR = Path(__file__).resolve().parents[2]

MODELS_DIR = BASE_DIR / "models"
SHARED_DIR = BASE_DIR / "shared"

EMOTION_MODEL_PATH = MODELS_DIR / "emotion_model.keras"
EYE_MODEL_PATH = MODELS_DIR / "eye_state_model.keras"
YOLO_PATH = MODELS_DIR / "yolov8n.pt"

CONTROL_PATH = SHARED_DIR / "session_control.json"
ATTENTION_PATH = SHARED_DIR / "attention_state.json"

os.makedirs(SHARED_DIR, exist_ok=True)
# print("CONTROL PATH:", CONTROL_PATH)

# ---------------- LOAD MODELS ----------------
yolo = YOLO(YOLO_PATH)
emotion_model = load_model(EMOTION_MODEL_PATH)
eye_model = load_model(EYE_MODEL_PATH)

emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# ---------------- STATE ----------------
cap = None
conf_count = 0
distract_count = 0
eye_closed_count = 0

CONFUSED_THRESHOLD = 3
DISTRACTED_THRESHOLD = 2
EYE_THRESHOLD = 15

attention_state = "Attentive"

# ---------------- MAIN LOOP ----------------
print("🧠 Attention Engine Running...")

while True:

    # ---------------- READ SESSION ----------------
    try:
        with open(CONTROL_PATH, "r") as f:
            studying = json.load(f).get("studying", False)
    except:
        studying = False

    # ---------------- START CAMERA ----------------
    if studying and cap is None:
        cap = cv2.VideoCapture(0)
        print("📷 Camera started")

    # ---------------- STOP CAMERA ----------------
    if not studying and cap is not None:
        cap.release()
        cap = None
        print("🛑 Camera stopped")
        time.sleep(1)
        continue

    if cap is None:
        time.sleep(0.5)
        continue

    ret, frame = cap.read()
    if not ret:
        continue

    # ---------------- FACE DETECTION ----------------
    results = yolo(frame, stream=True)
    faces = []

    for r in results:
        for box in r.boxes:
            if int(box.cls[0]) == 0:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                area = (x2 - x1) * (y2 - y1)
                faces.append((area, x1, y1, x2, y2))

    if not faces:
        continue

    faces.sort(reverse=True)
    _, x1, y1, x2, y2 = faces[0]

    face = frame[y1:y2, x1:x2]
    if face.size == 0:
        continue

    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

    # ---------------- EMOTION ----------------
    em = cv2.resize(gray, (48, 48)).reshape(1, 48, 48, 1) / 255.0
    pred = emotion_model.predict(em, verbose=0)[0]
    emotion = emotion_labels[np.argmax(pred)]

    # ---------------- EYE ----------------
    h, w = gray.shape
    eye_region = gray[int(h*0.25):int(h*0.45), int(w*0.15):int(w*0.85)]

    eye_state = "Unknown"
    if eye_region.size > 0:
        eye_img = cv2.resize(eye_region, (48, 48)).reshape(1, 48, 48, 1) / 255.0
        eye_pred = eye_model.predict(eye_img, verbose=0)[0]
        open_prob = eye_pred[1] if len(eye_pred) > 1 else eye_pred[0]

        if open_prob > 0.7:
            eye_state = "Open"
        elif open_prob < 0.3:
            eye_state = "Closed"

    # ---------------- LOGIC ----------------
    if emotion in ["Sad", "Fear"]:
        conf_count += 1
    elif emotion in ["Angry", "Disgust"]:
        distract_count += 1
    else:
        conf_count = max(0, conf_count - 1)
        distract_count = max(0, distract_count - 1)

    if eye_state == "Closed":
        eye_closed_count += 1
    else:
        eye_closed_count = 0

    if eye_closed_count >= EYE_THRESHOLD:
        attention_state = "Sleepy"
    elif distract_count >= DISTRACTED_THRESHOLD:
        attention_state = "Distracted"
    elif conf_count >= CONFUSED_THRESHOLD:
        attention_state = "Confused"
    else:
        attention_state = "Attentive"

    # ---------------- SAVE STATE ----------------
    with open(ATTENTION_PATH, "w") as f:
        json.dump({
            "attention": attention_state,
            "timestamp": time.time()
        }, f)

    # ---------------- DISPLAY ----------------
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
    cv2.putText(frame, f"{emotion} | {eye_state}", (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.putText(frame, f"Attention: {attention_state}", (20,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("Attention Engine", frame)

    if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
        break

# ---------------- CLEANUP ----------------
if cap:
    cap.release()
cv2.destroyAllWindows()

# print("ENGINE STARTED")
# print("LOADING MODELS...")
# print("CAMERA OPENING...")
# cap = cv2.VideoCapture(0)
# print("CAMERA STATUS:", cap.isOpened())