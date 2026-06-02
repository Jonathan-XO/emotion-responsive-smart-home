# 🏠 Emotion Responsive Smart Home

**An AI-powered, emotion-aware smart home automation system that adapts your environment based on your emotions and voice commands.**

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Arduino](https://img.shields.io/badge/Arduino-ESP8266/ESP32-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## 🌟 Key Features

✨ **Emotion Detection**: Real-time facial expression recognition (happy, sad, angry) using FER model  
🎙️ **Voice Interaction**: Natural speech-to-text and text-to-speech using Deepgram & Google APIs  
🤖 **Caring AI Assistant**: Context-aware responses with emotional intelligence (e.g., "You look sad, what happened?")  
💡 **Smart Home Control**: RGB lights, fan speed, LED control with real-time feedback  
🍕 **Contextual Actions**: Smart triggers (hungry → opens Swiggy, hot → max fan speed)  
🔒 **Educational Prototype**: This implementation uses cloud AI services (Gemini and Deepgram), but the architecture can be adapted to run fully offline using local AI models
📱 **Hardware Integration**: ESP8266/ESP32 with real-time device acknowledgment  
🧠 **AI Learning**: Pattern recognition and user adaptation over time  

## 📋 Project Structure

```
emotionresponse-smart-home/
├── ai/                    # Main AI assistant with emotion detection & voice processing
├── server/               # HTTP middleware server (bridges AI to ESP32)
├── esp32/                # ESP8266/ESP32 firmware for device control
├── docs/                 # Complete documentation
├── README.md             # This file
├── ARCHITECTURE.md       # System architecture & data flow
└── requirements.txt      # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- ESP8266/ESP32 microcontroller
- Webcam (for emotion detection)
- Microphone (for voice input)
- API Keys: [Google Gemini](https://ai.google.dev/) & [Deepgram](https://deepgram.com/)

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/Jonathan-XO/emotion-responsive-smart-home.git
cd emotion-responsive-smart-home
```

**2. Set up Python environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure API keys:**
```bash
cp ai/.env.example ai/.env  # Create your .env file
# Edit ai/.env with your API keys:
# GEMINI_API_KEY=your_key_here
# DEEPGRAM_API_KEY=your_key_here
```

**4. Start the server:**
```bash
python server/server.py
# Server running on http://localhost:8000
```

**5. Flash ESP8266/ESP32 firmware:**
- See [esp8266/README.md](esp8266/README.md) for detailed instructions

**6. Run the AI assistant:**
```bash
python ai/main.py
```

## 🏗️ Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│  Webcam +   │──→   │ Emotion      │      │   Voice      │
│ Microphone  │      │ Detection    │      │   Input      │
└─────────────┘      │ (FER Model)  │      │ (Deepgram)   │
                     └──────────────┘      └──────────────┘
                             │                      │
                             └──────────┬───────────┘
                                        │
                                        ↓
                             ┌──────────────────┐
                             │  Gemini AI Core  │
                             │  (Conversation   │
                             │  + Intent Parse) │
                             └──────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ↓                   ↓                   ↓
              ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
              │    Voice     │  │   External   │  │    HTTP      │
              │   Response   │  │     APIs     │  │    Server    │
              │   (gTTS)     │  │   (Swiggy)   │  │  (Middleware)│
              └──────────────┘  └──────────────┘  └──────────────┘
                    │                                      │
                    └──────────────────┬───────────────────┘
                                       │
                                       ↓
                            ┌──────────────────────┐
                            │  ESP8266/ESP32       │
                            │  - RGB Lights        │
                            │  - Fan Speed         │
                            │  - LED Control       │
                            └──────────────────────┘
                                       │
                                       ↓
                          ┌───────────────────────┐
                          │  Feedback ACK → AI    │
                          │  "Light turned on"    │
                          └───────────────────────┘
```

## 🎯 Use Cases

### Emotion-Based Environment
- **Happy** → Warm white lights, upbeat music
- **Sad** → Soft blue lights, comforting tone
- **Angry** → Cool lights, calm fan breeze

### Voice Commands
- "Turn on the lights"
- "Set fan to maximum"
- "What's the weather?"
- "I'm hungry" → Opens food delivery app
- "It's too hot" → Activates max fan speed

### Caring Assistant
```
You: "I feel tired"
Zasha: "You look a bit tired. Would you like me to dim the lights and turn on some relaxing music?"

You: "I'm hungry"
Zasha: "I recommend ordering something tasty!" [Opens Swiggy]

You: "It's so hot"
Zasha: "Let me turn on the fan at maximum speed to cool things down!"
```

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system design & data flow
- **[docs/SETUP.md](docs/SETUP.md)** - Step-by-step installation guide
- **[docs/HARDWARE.md](docs/HARDWARE.md)** - Hardware connections & pin configuration
- **[docs/API.md](docs/API.md)** - Complete API documentation
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues & solutions
- **[ai/README.md](ai/README.md)** - AI assistant setup
- **[server/README.md](server/README.md)** - Server documentation
- **[esp8266/README.md](esp8266/README.md)** - Firmware setup

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| **AI/ML** | Python, Google Gemini API, FER, OpenCV |
| **Voice** | Deepgram API (STT/TTS), gTTS |
| **Server** | Python HTTP server |
| **Firmware** | C++, ESP8266/ESP32, ArduinoJson |
| **Audio** | PyGame, sounddevice, websockets |

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👤 Author

**Jonathan-XO** - AI & IoT Enthusiast

## 🙏 Acknowledgments

- [Google Gemini API](https://ai.google.dev/) for conversational AI
- [Deepgram](https://deepgram.com/) for speech processing
- [FER](https://github.com/justinshenk/fer) for emotion detection
- [ArduinoJson](https://arduinojson.org/) for JSON parsing

## 📞 Support

For issues, questions, or suggestions:
- Open an [GitHub Issue](https://github.com/Jonathan-XO/emotion-responsive-smart-home/issues)
- Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

---

**Made with ❤️ for smarter, more empathetic homes**
