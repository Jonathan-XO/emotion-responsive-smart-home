import os
import asyncio
import websockets
import sounddevice as sd
import numpy as np
import json
import requests
from google import genai
from gtts import gTTS
import io
import pygame
import threading
import queue
import time
import cv2
from fer import FER
import webbrowser

# ============================================================
# EMOTION RESPONSIVE SMART HOME - AI ASSISTANT CORE
# ============================================================
# This module handles:
# - Facial emotion detection (FER model)
# - Speech-to-Text (Deepgram WebSocket)
# - Conversational AI (Google Gemini)
# - Text-to-Speech (gTTS)
# - Device control intent parsing
# - Caring assistant behavior
# ============================================================

# -------- CONFIG --------
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "your_deepgram_key_here")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_gemini_key_here")
ESP32_URL = "http://192.168.37.165:8000/get_command"  # Server URL

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_key_here":
    raise ValueError("Set GEMINI_API_KEY in environment variables")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
COMPANION_NAME = "Zasha"  # AI Assistant name

# Conversation history for context
conversation_history = [
    {"role": "system", "content": f"You are {COMPANION_NAME}, a friendly home assistant. Keep responses very short and small, interactive, and funny. Do not use emojis. if user asks who are you just introduce your name and what you can do as a home assistant"}
]

# Thread safety for conversation history
convo_lock = threading.Lock()

# State management
mic_muted = False
tts_queue = queue.Queue()
pygame.mixer.init()

# -------- DEVICE CONTROL --------
def send_to_dummy_server(cmd):
    """Send JSON command to middleware server."""
    try:
        resp = requests.post(ESP32_URL, json=cmd, timeout=1)
        print("Server Response:", resp.text)
        return True
    except Exception as e:
        print("Error sending to server:", e)
        return False

# -------- INTENT PARSER --------
def parse_user_command(user_text):
    """Parse user commands for device control."""
    user_text = user_text.lower()
    cmd = None
    feedback = None

    # FAN control
    if "fan" in user_text:
        if any(word in user_text for word in ["off", "stop", "disable"]):
            cmd = {"device": "fan", "speed": 0}
            feedback = "Fan turned off."
        else:
            speed = 50
            if any(word in user_text.lower() for word in ["fast", "max", "maximum", "full"]):
                speed = 255
            elif any(word in user_text.lower() for word in ["medium", "half"]):
                speed = 128
            elif any(word in user_text.lower() for word in ["slow", "low"]):
                speed = 64
            cmd = {"device": "fan", "speed": speed}
            feedback = f"Fan speed set to {speed}."

    # RGB light control
    elif "light" in user_text or "rgb" in user_text:
        if any(word in user_text for word in ["off", "disable"]):
            cmd = {"device": "rgb", "r": 0, "g": 0, "b": 0}
            feedback = "RGB lights turned off."
        else:
            colors = {
                "red": {"r": 255, "g": 0, "b": 0},
                "green": {"r": 0, "g": 255, "b": 0},
                "blue": {"r": 0, "g": 0, "b": 255},
                "yellow": {"r": 255, "g": 255, "b": 0},
                "purple": {"r": 128, "g": 0, "b": 128},
                "white": {"r": 255, "g": 225, "b": 200}
            }
            for name, val in colors.items():
                if name in user_text:
                    cmd = {"device": "rgb", **val}
                    feedback = f"RGB light set to {name}."
                    break
            else:
                cmd = {"device": "rgb", "r": 255, "g": 255, "b": 255}
                feedback = "RGB light set to white."

    # LED on/off
    elif "led" in user_text:
        if "on" in user_text:
            cmd = {"device": "led", "action": "on"}
            feedback = "LED turned on."
        elif "off" in user_text:
            cmd = {"device": "led", "action": "off"}
            feedback = "LED turned off."

    return cmd, feedback

# -------- WEATHER --------
def get_weather_and_reply(user_text):
    """Get weather and generate AI response."""
    coords = {"Bangalore": (12.9716, 77.5946)}
    lat, lon = coords.get("Bangalore", (12.9716, 77.5946))
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "rain", "windspeed_10m"],
        "daily": ["uv_index_max", "temperature_2m_max", "temperature_2m_min"],
        "timezone": "Asia/Kolkata"
    }
    response = requests.get(url, params=params).json()
    daily = response.get("daily", {})
    temp_min = daily.get("temperature_2m_min", ["N/A"])[0]
    temp_max = daily.get("temperature_2m_max", ["N/A"])[0]
    uv = daily.get("uv_index_max", ["N/A"])[0]
    
    prompt = (
        f"The user asked about the weather in Bangalore. "
        f"Daily weather: temperature {temp_min}-{temp_max}°C, UV index {uv}. "
        "Respond in a short, friendly, funny way. Keep it conversational."
    )
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt]
    )
    return response.text

# -------- GEMINI AI --------
def ask_gemini(prompt):
    """Query Gemini AI with thread-safe conversation history."""
    with convo_lock:
        conversation_history.append({"role": "user", "content": prompt})
        contents = [msg["content"] for msg in conversation_history]
    
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )
    
    with convo_lock:
        conversation_history.append({"role": "assistant", "content": response.text})
    
    return response.text

def gemini_enqueue_and_tts(prompt):
    """Run Gemini query and enqueue result for TTS."""
    try:
        resp = ask_gemini(prompt)
        tts_queue.put(resp)
    except Exception as e:
        print("Error in gemini_enqueue_and_tts:", e)

# -------- CARING / EMOTION --------
async def handle_caring(user_text):
    """Handle caring assistant responses to user context."""
    try:
        prompt = (
            f"You observe the user directly. "
            f"The user said: '{user_text}'. Respond in a short, lively, and caring way."
        )
        asyncio.create_task(asyncio.to_thread(gemini_enqueue_and_tts, prompt))

        # Hunger trigger
        if "hungry" in user_text.lower():
            dish_prompt = "Suggest a tasty dish for the user to order right now."
            asyncio.create_task(asyncio.to_thread(gemini_enqueue_and_tts, dish_prompt))
            print(f"{COMPANION_NAME}: I suggest ordering something tasty.")
            webbrowser.open("https://www.swiggy.com/")

        # Hot/cold triggers
        if "hot" in user_text.lower():
            asyncio.create_task(asyncio.to_thread(send_to_dummy_server, {"device": "fan", "speed": 255}))
        if "cold" in user_text.lower():
            asyncio.create_task(asyncio.to_thread(send_to_dummy_server, {"device": "heater", "action": "on"}))

    except Exception as e:
        print("Error handling caring:", e)

async def handle_emotion(emotion):
    """Handle emotion-based environment adaptation."""
    try:
        prompt = f"You observe the user. They look {emotion}. Respond lively and friendly."
        asyncio.create_task(asyncio.to_thread(gemini_enqueue_and_tts, prompt))
    except Exception as e:
        print("Error handling emotion:", e)

# -------- DECISION LOGIC --------
async def process_user_input(user_text):
    """Route user input to appropriate handler."""
    control_keywords = ["light", "led", "fan", "color", "speed", "on", "off"]
    caring_triggers = ["hungry", "thirsty", "tired", "hot", "cold", "sad", "angry", "happy"]

    lower_text = user_text.lower()

    # Device control
    if any(word in lower_text for word in control_keywords):
        command, feedback = parse_user_command(user_text)
        if command:
            send_to_dummy_server(command)
            if feedback:
                tts_queue.put(feedback)
                followup_prompt = (
                    f"The user changed {command.get('device')}. {feedback} "
                    "Respond lively and friendly."
                )
                asyncio.create_task(asyncio.to_thread(gemini_enqueue_and_tts, followup_prompt))
        return
    
    # Caring triggers
    if any(word in lower_text for word in caring_triggers):
        asyncio.create_task(handle_caring(user_text))
        return

    # Weather
    if "weather" in lower_text:
        def weather_task():
            try:
                reply = get_weather_and_reply(user_text)
                tts_queue.put(reply)
            except Exception as e:
                print("Weather task error:", e)
        asyncio.create_task(asyncio.to_thread(weather_task))
    else:
        # General conversation
        asyncio.create_task(asyncio.to_thread(gemini_enqueue_and_tts, user_text))

# -------- TTS --------
def tts_worker():
    """TTS worker thread - processes queue and plays audio."""
    global mic_muted
    while True:
        text = tts_queue.get()
        if text is None:
            break
        mic_muted = True
        try:
            tts = gTTS(text=text, lang='en', tld='com')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print("TTS error:", e)
        mic_muted = False

# -------- STT --------
async def stream_audio():
    """Stream audio from microphone to Deepgram for STT."""
    global mic_muted
    uri = "wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000&channels=1&punctuate=true"

    while True:
        try:
            async with websockets.connect(uri, extra_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}) as ws:
                print("Listening...")
                loop = asyncio.get_running_loop()

                def callback(indata, frames, time_, status):
                    audio_bytes = np.zeros_like(indata, dtype=np.int16).tobytes() if mic_muted else indata.copy().astype(np.int16).tobytes()
                    asyncio.run_coroutine_threadsafe(ws.send(audio_bytes), loop)

                with sd.InputStream(samplerate=16000, channels=1, dtype='int16', callback=callback):
                    last_transcript = ""
                    async for msg in ws:
                        data = json.loads(msg)
                        transcript = data.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
                        if transcript and transcript != last_transcript:
                            last_transcript = transcript
                            print("STT:", transcript)
                            await process_user_input(transcript)

        except websockets.ConnectionClosed:
            print("Deepgram connection closed. Reconnecting in 2s...")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Unexpected STT error: {e}. Reconnecting in 2s...")
            await asyncio.sleep(2)
        except KeyboardInterrupt:
            break

# -------- FACIAL EMOTION --------
def facial_expression_worker(loop):
    """Worker thread for emotion detection via facial expressions."""
    cap = cv2.VideoCapture(0)
    detector = FER(mtcnn=False)

    frame_id = 0
    prev_sent_emotion = None
    candidate_emotion = None
    candidate_score = 0
    candidate_start_time = 0
    stable_time = 2.0  # Emotion must be stable for 2 seconds

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            display_frame = cv2.resize(frame, (640, 480))
            frame_id += 1

            # Process every 5 frames for efficiency
            if frame_id % 5 == 0:
                emotion, score = detector.top_emotion(display_frame)
                current_time = time.time()

                if emotion and emotion.lower() in ["happy", "sad", "angry"]:
                    # New candidate emotion or change
                    if candidate_emotion != emotion:
                        candidate_emotion = emotion
                        candidate_score = score
                        candidate_start_time = current_time
                    else:
                        # Check if stable
                        if (current_time - candidate_start_time) >= stable_time:
                            # Only send if different from last sent
                            if candidate_emotion != prev_sent_emotion:
                                prev_sent_emotion = candidate_emotion
                                print(f"[Emotion] Stable detected: {candidate_emotion} ({candidate_score:.2f})")
                                asyncio.run_coroutine_threadsafe(handle_emotion(candidate_emotion.lower()), loop)
                                # Reset candidate
                                candidate_emotion = None

                # Display for debug
                if emotion:
                    label = f"{emotion} ({score:.2f})"
                    cv2.putText(display_frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Webcam - Emotion Detection", display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

# -------- MAIN --------
if __name__ == "__main__":
    print(f"🏠 {COMPANION_NAME} - Emotion Responsive Smart Home Assistant")
    print("Starting up...\n")
    
    loop = asyncio.get_event_loop()

    # Start TTS worker thread
    tts_thread = threading.Thread(target=tts_worker, daemon=True)
    tts_thread.start()

    # Start emotion detection thread
    facial_thread = threading.Thread(target=facial_expression_worker, args=(loop,), daemon=True)
    facial_thread.start()

    # Start STT stream
    asyncio.ensure_future(stream_audio())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    finally:
        tts_queue.put(None)
        tts_thread.join()
