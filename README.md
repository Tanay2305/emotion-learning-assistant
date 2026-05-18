AI Emotion-Aware Learning Assistant

An intelligent learning assistant that monitors student attention in real-time using computer vision and adapts interaction through voice-based feedback.

Features
Real-time face detection using YOLOv8
Emotion recognition
Eye-state detection
Attention classification:
Attentive
Distracted
Confused
Sleepy
Voice-based question answering
Interactive Streamlit interface
Study session monitoring

Tech Stack
Python
Streamlit
TensorFlow / Keras
OpenCV
YOLOv8
Scikit-learn
Speech Recognition

Architecture

Streamlit UI
   ↓
Session Control
   ↓
Attention Engine
   ↓
Emotion + Eye Detection
   ↓
Attention State
   ↓
Voice Feedback

Run Project
Start attention engine
python app/engines/attention_engine.py
Start UI
streamlit run app/ui/streamlit_app.py