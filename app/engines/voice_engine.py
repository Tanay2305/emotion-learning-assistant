import pyttsx3
import speech_recognition as sr

def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except RuntimeError:
        pass


def listen():
    r = sr.Recognizer()
    r.energy_threshold = 300
    r.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=5, phrase_time_limit=6)
        return r.recognize_google(audio)
    except:
        return None