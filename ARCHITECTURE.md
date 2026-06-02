# 🏗️ System Architecture

## Overview

The Emotion Responsive Smart Home system is built on a modular, privacy-first architecture that processes emotions and voice commands locally while maintaining real-time hardware control through a polling-based middleware server.

## System Components

### 1. **AI Assistant Core** (`ai/main.py`)
- **Emotion Detection**: Facial Expression Recognition using FER model
- **Speech Processing**: Deepgram WebSocket for real-time STT
- **Conversation Engine**: Google Gemini API for context-aware responses
- **Text-to-Speech**: gTTS for audio feedback
- **Intent Parser**: Analyzes commands for device control
- **Caring Logic**: Emotional awareness and contextual responses

### 2. **Middleware Server** (`server/server.py`)
- Acts as a bridge between AI and Hardware
- Receives device control commands from AI
- Maintains real-time device states
- Serves state updates to ESP8266/ESP32
- Enables Hardware → AI feedback loop

### 3. **Hardware Controller** (`esp32/smart_home.ino`)
- Polls server every 800ms for state changes
- Executes device control commands (PWM, digital I/O)
- Manages RGB LEDs, Fan, LED outputs
- Provides device acknowledgment feedback

## Data Flow Diagrams

### Flow 1: Emotion Detection & Response

```
┌─────────────────────────────────────────────────────────────┐
│ EMOTION DETECTION FLOW                                      │
└─────────────────────────────────────────────────────────────┘

  Webcam Input
      │
      ↓
  ┌──────────────────────┐
  │ OpenCV Frame Capture │
  │ (Every 5 frames)     │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ FER Model Analysis   │
  │ Detect: Happy/Sad/   │
  │         Angry        │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ Stability Check      │
  │ (2 second threshold) │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ Send to Gemini AI    │
  │ "They look HAPPY"    │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ Generate Response    │
  │ + Enqueue to TTS     │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ Execute Device       │
  │ Control Actions      │
  │ (lights, fan, etc)   │
  └──────────────────────┘
```

### Flow 2: Voice Command Processing

```
┌─────────────────────────────────────────────────────────────┐
│ VOICE COMMAND FLOW                                          │
└─────────────────────────────────────────────────────────────┘

  Microphone Input (16kHz, mono)
      │
      ↓
  ┌──────────────────────┐
  │ Deepgram WebSocket   │
  │ Speech-to-Text       │
  │ Stream continuously  │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ Text Received        │
  │ "Turn on the lights" │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ Intent Classification│
  │ - Device Control?    │
  │ - Caring Trigger?    │
  │ - Conversational?    │
  │ - Weather query?     │
  └──────────────────────┘
      │
      ├─────────────┬──────────────┬──────────────┬─────────────┐
      │             │              │              │             │
      ↓             ↓              ↓              ↓             ↓
   Device      Caring       Conversational   Weather     External API
   Control     Trigger      Query           Query        (Swiggy)
      │             │              │              │             │
      ↓             ↓              ↓              ↓             ↓
  Parse        Handle         Ask Gemini      Get Weather   Open Browser
  Command      Emotion        Response         + Respond    Swiggy
      │             │              │              │             │
      └─────────────┴──────────────┴──────────────┴─────────────┘
              │
              ↓
      ┌──────────────────────┐
      │ Send to HTTP Server  │
      │ (if device control)  │
      └──────────────────────┘
              │
              ↓
      ┌──────────────────────┐
      │ Enqueue Response     │
      │ to TTS Queue         │
      └──────────────────────┘
              │
              ↓
      ┌──────────────────────┐
      │ gTTS Audio Reply     │
      │ Play via PyGame      │
      └──────────────────────┘
```

### Flow 3: Device Control Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ DEVICE CONTROL FLOW                                         │
└─────────────────────────────────────────────────────────────┘

  AI Command
  "Turn on lights"
      │
      ↓
  ┌──────────────────────┐
  │ Intent Parser        │
  │ Identify device,     │
  │ color, state         │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐     ┌──────────────────────┐
  │ Build JSON Command   │────→│ Example JSON:        │
  │ {                    │     │ {                    │
  │   "device": "rgb",   │     │   "device": "rgb",   │
  │   "r": 255,          │     │   "r": 255,          │
  │   "g": 200,          │     │   "g": 200,          │
  │   "b": 100           │     │   "b": 100           │
  │ }                    │     │ }                    │
  └──────────────────────┘     └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ HTTP POST to Server  │
  │ http://localhost:8000│
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ Server Updates State │
  │ device_states["rgb"] │
  └──────────────────────┘
      │
      ├──→ Response to AI: "Success"
      │
      ↓
  ┌──────────────────────┐
  │ ESP8266 Polls Server │
  │ GET /get_command     │
  │ (every 800ms)        │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ ESP8266 Receives     │
  │ Updated RGB State    │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ Execute PWM Control  │
  │ analogWrite(R_PIN,   │
  │ analogWrite(G_PIN,   │
  │ analogWrite(B_PIN,   │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ RGB LED Turns ON     │
  │ Color: Warm White    │
  └──────────────────────┘
      │
      └──→ (Optional) Feedback → AI
             "Light turned on"
```

### Flow 4: Caring Assistant Trigger

```
┌─────────────────────────────────────────────────────────────┐
│ CARING ASSISTANT FLOW (Example: Hunger)                    │
└─────────────────────────────────────────────────────────────┘

  User Says
  "I'm hungry"
      │
      ↓
  ┌──────────────────────┐
  │ STT: "I'm hungry"    │
  └──────────────────────┘
      │
      ↓
  ┌──────────────────────┐
  │ Check Keywords       │
  │ "hungry" found ✓     │
  └──────────────────────┘
      │
      ├─→ Gemini Prompt:
      │   "User says they're hungry.
      │    Respond caringly and
      │    suggest dishes."
      │
      ├─→ Response: "I suggest ordering
      │              something tasty!"
      │
      └─→ Open Browser: Swiggy
             webbrowser.open(
             "https://www.swiggy.com/"
             )
      │
      ↓
  ┌──────────────────────┐
  │ TTS: "I suggest..."
  │ Play Audio Response  │
  └──────────────────────┘
```

## Thread Architecture

The system uses multi-threaded architecture for non-blocking operations:

```
┌─────────────────────────────────────────────┐
│ MAIN THREAD (Event Loop)                    │
│ - Asyncio Event Loop                        │
│ - Coordinates all async operations          │
└─────────────────────────────────────────────┘
        │
        ├─→ ┌──────────────────────┐
        │   │ STT Thread           │
        │   │ Deepgram WebSocket   │
        │   │ Continuous listening │
        │   └──────────────────────┘
        │
        ├─→ ┌──────────────────────┐
        │   │ TTS Thread           │
        │   │ gTTS Queue Consumer  │
        │   │ Daemon thread        │
        │   └──────────────────────┘
        │
        └─→ ┌──────────────────────┐
            │ Emotion Thread       │
            │ FER Model Processing │
            │ Webcam capture       │
            └──────────────────────┘
```

## Server Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ HTTP MIDDLEWARE SERVER                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PORT 8000                                                  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Device State Store                                   │  │
│  │ {                                                    │  │
│  │   "led": {"device": "led", "action": "off"},       │  │
│  │   "rgb": {"device": "rgb", "r": 0, "g": 0, ...}, │  │
│  │   "fan": {"device": "fan", "speed": 0}            │  │
│  │ }                                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  POST /  (Receive commands from AI)                         │
│  └─→ Update device states                                  │
│  └─→ Return confirmation                                   │
│                                                             │
│  GET /get_command  (ESP32 polls here)                       │
│  └─→ Return current device states                          │
│  └─→ ESP32 polls every 800ms                               │
│                                                             │
│  GET /ping  (Health check)                                  │
│  └─→ Return "alive" status                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Hardware Integration

```
┌─────────────────────────────────────────────────────────────┐
│ ESP8266/ESP32 FIRMWARE                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WiFi Connection (192.168.37.165:8000)                      │
│  │                                                          │
│  ├─→ Poll Loop (800ms intervals)                            │
│  │   ├─→ GET /get_command from Server                       │
│  │   ├─→ Parse JSON response                                │
│  │   └─→ Update device states                               │
│  │                                                          │
│  ├─→ LED Control (Digital I/O)                              │
│  │   ├─→ D4 (GPIO2): Onboard LED (active LOW)              │
│  │   ├─→ digitalWrite(LED_PIN, LOW/HIGH)                    │
│  │   └─→ Feedback: LED on/off                               │
│  │                                                          │
│  ├─→ RGB Control (PWM)                                      │
│  │   ├─→ D6 (GPIO12): Red channel                            │
│  │   ├─→ D7 (GPIO13): Green channel                          │
│  │   ├─→ D8 (GPIO15): Blue channel                           │
│  │   ├─→ analogWrite(R_PIN, 0-255)                          │
│  │   └─→ Feedback: Color set                                │
│  │                                                          │
│  ├─→ Fan Control (PWM)                                      │
│  │   ├─→ D1 (GPIO5): Fan speed                              │
│  │   ├─→ analogWrite(FAN_PIN, 0-255)                        │
│  │   ├─→ Speed: 0=off, 64=low, 128=med, 255=max            │
│  │   └─→ Feedback: Speed set                                │
│  │                                                          │
│  └─→ Serial Output (115200 baud)                            │
│      └─→ Debug logs                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Emotion-Action Mappings

```
┌─────────────┬──────────────────────┬──────────────────────┐
│  Emotion    │  Device Actions      │  AI Response         │
├─────────────┼──────────────────────┼──────────────────────┤
│  HAPPY      │ - Warm white light   │ "You're looking      │
│             │ - Fan: low           │  cheerful! Keep it   │
│             │ - RGB: yellow/warm   │  up!"                │
├─────────────┼──────────────────────┼──────────────────────┤
│  SAD        │ - Soft blue light    │ "I notice you seem   │
│             │ - Fan: off           │  down. What's        │
│             │ - RGB: cool tones    │  bothering you?"     │
├─────────────┼──────────────────────┼──────────────────────┤
│  ANGRY      │ - Cool bright light  │ "You seem upset.      │
│             │ - Fan: max speed     │  Let me help calm    │
│             │ - RGB: cool colors   │  things down."       │
└─────────────┴──────────────────────┴──────────────────────┘
```

## Caring Triggers

```
┌──────────────┬──────────────────────┬──────────────────────┐
│  User Says   │  Trigger Actions     │  AI Behavior         │
├──────────────┼──────────────────────┼──────────────────────┤
│  "Hungry"    │ - Open Swiggy        │ "Let me help you     │
│              │ - Ask Gemini for     │  find something     │
│              │   dish suggestions   │  delicious!"        │
├──────────────┼──────────────────────┼──────────────────────┤
│  "Hot"       │ - Fan: max (255)     │ "Turning on the      │
│              │ - RGB: cool blue     │  fan to full blast!" │
├──────────────┼──────────────────────┼──────────────────────┤
│  "Cold"      │ - Heater: ON         │ "Let me warm things  │
│              │ - RGB: warm orange   │  up for you."        │
├──────────────┼──────────────────────┼──────────────────────┤
│  "Tired"     │ - Dim lights         │ "Get some rest. I'll │
│              │ - Fan: low           │  keep things calm."  │
│              │ - RGB: soft colors   │                      │
└──────────────┴──────────────────────┴──────────────────────┘
```

## Security & Privacy

- ✅ **Offline First**: Core AI processing happens locally
- ✅ **No Video Upload**: Emotion detection is local-only
- ✅ **No Audio Storage**: Voice is streamed, not stored
- ✅ **Local Network**: Server runs on private network only
- ✅ **No Cloud Dependencies**: Can work without internet (except APIs)

## Performance Considerations

| Component | Frequency | Impact |
|-----------|-----------|--------|
| Emotion detection | Every 5 frames (≈6x/sec) | Low CPU impact |
| STT streaming | Continuous | Network dependent |
| Gemini API calls | Per command | 1-2 sec latency |
| ESP32 polling | Every 800ms | Minimal network load |
| TTS generation | Per response | 1-2 sec latency |

## Future Enhancements

- 🔄 Multi-device support (multiple rooms)
- 🧠 On-device ML model optimization
- 📊 User behavior analytics
- 🎵 Spotify integration for mood-based music
- 💨 Scent diffuser control
- 🌡️ Temperature sensor feedback
- 📱 Mobile app control
- 🔐 User authentication

---

For more details, see individual module documentation:
- [ai/README.md](ai/README.md)
- [server/README.md](server/README.md)
- [esp32/README.md](esp32/README.md)
