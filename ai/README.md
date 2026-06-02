# 🤖 AI Assistant Module - Emotion Responsive Smart Home

## Overview

The **AI Assistant** is the intelligent brain of the emotion-responsive smart home system. It handles:

- 🎙️ **Voice Recognition** - Real-time speech-to-text via Deepgram WebSocket
- 🧠 **Conversational AI** - Context-aware responses using Google Gemini API
- 😊 **Emotion Detection** - Facial expression recognition using FER model
- 🗣️ **Text-to-Speech** - Natural voice output via gTTS
- 🏠 **Device Control** - Intelligent intent parsing for smart home devices
- 💚 **Caring Behavior** - Contextual responses based on user emotions and needs

## Architecture

```
┌─────────────────────────────────────┐
│   Main AI Loop (main.py)            │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ STT Thread   │  │ TTS Thread  │ │
│  │ (Deepgram)   │  │ (gTTS)      │ │
│  └──────────────┘  └─────────────┘ │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ Emotion      │  │ Intent      │ │
│  │ Detection    │  │ Parser      │ │
│  │ (FER)        │  │             │ │
│  └──────────────┘  └─────────────┘ │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │ Gemini AI    │  │ Device      │ │
│  │ (LLM)        │  │ Controller  │ │
│  └──────────────┘  └─────────────┘ │
│                                     │
└─────────────────────────────────────┘
        │
        │ HTTP POST
        ▼
    Middleware Server (port 8000)
        │
        │ HTTP GET (polling)
        ▼
    ESP8266/ESP32 (Device Control)
```

## Components

### 1. **Speech-to-Text (STT) - Deepgram**

Real-time voice input processing:

```python
async def stream_audio():
    """Stream audio from microphone to Deepgram for STT."""
    uri = "wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000&channels=1&punctuate=true"
    # WebSocket connection for real-time transcription
```

**Features:**
- Real-time streaming via WebSocket
- 16kHz PCM audio format
- Automatic punctuation
- Fallback reconnection on disconnect

### 2. **Facial Emotion Detection - FER Model**

Detects user emotions from webcam:

```python
def facial_expression_worker(loop):
    """Worker thread for emotion detection via facial expressions."""
    detector = FER(mtcnn=False)
    # Processes frames, identifies: Happy, Sad, Angry, etc.
    # 2-second stability filter to avoid false positives
```

**Features:**
- Real-time webcam processing
- Emotion stability filter (2 seconds)
- Asynchronous event triggering
- Efficient frame sampling (every 5th frame)

### 3. **Conversational AI - Google Gemini**

Context-aware dialogue:

```python
def ask_gemini(prompt):
    """Query Gemini AI with thread-safe conversation history."""
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )
```

**Features:**
- Maintains conversation history for context
- Thread-safe operation
- Short, friendly responses
- Smart device control assistance

### 4. **Text-to-Speech - gTTS**

Audio output generation:

```python
def tts_worker():
    """TTS worker thread - processes queue and plays audio."""
    # Converts text to MP3
    # Plays via pygame mixer
    # Mutes microphone during playback
```

**Features:**
- Queue-based processing
- Automatic mic muting during playback
- Google TTS (free, no API key)
- Natural sounding voices

### 5. **Intent Parser**

Extracts device control commands from natural language:

```python
def parse_user_command(user_text):
    """Parse user commands for device control."""
    # Recognizes: "turn on light", "fan speed high", etc.
    # Returns: JSON device command
```

**Supported Commands:**
- 🔌 **Fan Control**: "turn on fan", "fan speed high/medium/low/max", "turn off fan"
- 💡 **RGB Light**: "light red/green/blue/yellow/purple/white", "turn off light"
- 🔴 **LED Control**: "turn on LED", "turn off LED"

### 6. **Caring Assistant Behavior**

Contextual responses based on user state:

```python
async def handle_caring(user_text):
    """Handle caring assistant responses to user context."""
    if "hungry" in user_text.lower():
        # Suggests food delivery (opens Swiggy)
    if "hot" in user_text.lower():
        # Turns on fan to max
    if "cold" in user_text.lower():
        # Activates heater
```

**Triggers:**
- 🍽️ **Hunger**: Suggests restaurants, opens food delivery app
- 🥵 **Heat**: Activates fan at maximum speed
- ❄️ **Cold**: Turns on heater
- 😢 **Sadness**: Caring responses, emotional support
- 😡 **Anger**: Calming, soothing responses

## Installation

### Prerequisites

- Python 3.8+
- Webcam (for emotion detection)
- Microphone
- Speaker/Audio output
- WiFi connection

### Setup Steps

1. **Install Dependencies**
   ```bash
   cd ai
   pip install -r requirements.txt
   ```

2. **Get API Keys**
   - [Google Gemini API Key](https://aistudio.google.com/app/apikey)
   - [Deepgram API Key](https://console.deepgram.com/)

3. **Set Environment Variables**
   ```bash
   export GEMINI_API_KEY="your_key_here"
   export DEEPGRAM_API_KEY="your_key_here"
   ```

4. **Update Server URL**
   ```python
   ESP32_URL = "http://YOUR_SERVER_IP:8000/get_command"
   ```

5. **Run the Assistant**
   ```bash
   python main.py
   ```

## Usage

### Starting the Assistant

```bash
python main.py
```

**Output:**
```
🏠 Zasha - Emotion Responsive Smart Home Assistant
Starting up...

Listening...
STT: turn on the light
🌈 RGB: R=255, G=0, B=0
Zasha: Light turned red! Perfect for your mood.
```

### Voice Commands

**Device Control:**
- "Turn on the light"
- "Set light to blue"
- "Fan speed high"
- "Turn off the LED"

**Casual Chat:**
- "What's the weather?"
- "I'm hungry"
- "Tell me a joke"
- "How are you?"

**Emotion-Triggered:**
- "I'm sad" → Assistant offers support
- "I'm so hot" → Fan turns on automatically
- "I'm cold" → Heater activates

## Configuration

Edit `main.py` to customize:

```python
COMPANION_NAME = "Zasha"              # Assistant name
ESP32_URL = "http://192.168.37.165:8000/get_command"  # Server URL
GEMINI_API_KEY = os.getenv(...)       # AI API key
DEEPGRAM_API_KEY = os.getenv(...)     # Speech API key
```

## Thread Safety

All shared resources are protected with locks:

```python
convo_lock = threading.Lock()  # Protects conversation history
tts_queue = queue.Queue()      # Thread-safe audio queue
```

## Performance

- **STT Latency**: < 1s (Deepgram)
- **Emotion Detection**: ~100ms per frame (FER)
- **AI Response Time**: 1-3s (Gemini)
- **TTS Generation**: 2-5s (gTTS)
- **Overall Response**: < 10 seconds

## Troubleshooting

### Microphone Not Working
```bash
# Check available devices
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### Deepgram Connection Error
- Verify API key is set
- Check internet connection
- Try re-running the script (auto-reconnect in 2s)

### Emotion Detection No Frames
- Check webcam is working: `python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"`
- Ensure good lighting
- Check FER model can see your face

### Gemini API Errors
- Verify API key: `echo $GEMINI_API_KEY`
- Check quota at [Google Cloud Console](https://console.cloud.google.com/)
- Ensure internet connection

## Dependencies

See `requirements.txt`:

```
google-genai==0.3.0          # Google Gemini API
deepgram-sdk==3.4.0          # Deepgram Speech API
sounddevice==0.4.6           # Microphone input
numpy==1.24.3                # Audio processing
gTTS==2.3.2                  # Text-to-Speech
pygame==2.5.0                # Audio playback
opencv-python==4.8.0.76      # Webcam access
fer==22.4.3                  # Emotion detection
websockets==11.0.3           # WebSocket client
requests==2.31.0             # HTTP requests
```

## Future Enhancements

- 🎵 Voice clone for personalized responses
- 📊 Emotion tracking over time
- 🧠 Custom ML models for specific domains
- 🌍 Multi-language support
- 🔐 Privacy mode (local processing only)
- 📱 Mobile app integration

## Architecture Decisions

### Why Async/Threading?

- **STT Streaming**: Must be real-time, non-blocking
- **Emotion Detection**: Continuous background monitoring
- **TTS Playback**: Blocks microphone input to avoid feedback
- **Gemini AI**: Network I/O can be slow, don't block other tasks

### Why Stability Filter for Emotions?

Without filtering, faces making brief expressions trigger false responses. The 2-second stability filter ensures only genuine emotion states trigger actions.

### Why Polling Architecture?

The middleware uses polling instead of WebSocket to the ESP32 because:
- Simple HTTP GET is more reliable on resource-constrained devices
- No need for persistent connections on embedded boards
- Easy to scale to multiple devices

## License

MIT License - See repository for details

## Author

Jonathan-XO - AI Assistant Module
Part of the Emotion-Responsive Smart Home project

---

**Questions or Issues?** Check the [Troubleshooting Guide](../TROUBLESHOOTING.md) or open an issue on GitHub!
