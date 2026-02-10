# J.A.R.V.I.S - Real-Life AI Desktop Assistant

A modular AI assistant inspired by Iron Man's J.A.R.V.I.S, featuring voice interaction, task automation, and real-time information retrieval.

## Project Structure

```
jarvis/
├── backend/                    # FastAPI Backend Server
│   ├── main.py                 # FastAPI app with WebSocket endpoint
│   ├── requirements.txt        # Backend dependencies
│   ├── brain/
│   │   ├── __init__.py
│   │   └── router.py           # Decision Making Model (query classification)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── stt_service.py      # Speech-to-Text (faster-whisper)
│   │   ├── tts_service.py      # Text-to-Speech (edge-tts)
│   │   └── chat_service.py     # LLM Chat Service (OpenAI-compatible)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── automation.py       # System automation (apps, websites, reminders)
│   │   └── realtime.py         # Web search and live info
│   └── data/                   # Auto-created for notes/reminders
│
├── frontend/                   # PyQt5 Desktop GUI
│   ├── main.py                 # Application entry point
│   ├── requirements.txt        # Frontend dependencies
│   ├── ui/
│   │   ├── __init__.py
│   │   └── main_window.py      # Main application window
│   └── widgets/
│       ├── __init__.py
│       ├── chat_bubble.py      # Chat message bubbles
│       ├── status_indicator.py # Status display (Idle/Listening/etc)
│       ├── mic_button.py       # Microphone button with animation
│       └── audio_recorder.py   # Audio recording handler
│
├── shared/                     # Shared code between frontend/backend
│   ├── __init__.py
│   └── schemas.py              # Message types, status enums, schemas
│
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Features

### Core Loop
1. **Listen** - Click mic button to record voice (or type text)
2. **Understand** - Whisper transcribes speech, Brain classifies intent
3. **Respond** - Appropriate handler generates response
4. **Speak** - edge-tts converts response to natural speech

### Query Classification (Brain Router)
- **GENERAL_QUERY** - Normal chat/knowledge questions → LLM response
- **REALTIME_QUERY** - Live info (news, weather, search) → Web search + summarize
- **AUTOMATION_QUERY** - Task execution → Opens apps/websites, sets reminders, takes notes

### Automation Tools
- `open_website(url)` - Opens URL in default browser
- `open_app(name)` - Launches applications (Windows/Mac/Linux support)
- `set_reminder(text, minutes)` - Sets a reminder
- `take_note(text)` - Saves note to local JSON file
- `get_time()` / `get_date()` - Returns current time/date

### Example Commands
```
"Open YouTube"                    → Opens youtube.com
"Launch notepad"                  → Opens Notepad
"Remind me to take a break in 30 minutes"  → Sets reminder
"Take note: buy groceries"        → Saves note
"What's the weather today?"       → Web search + summary
"Search for Python tutorials"     → Web search
"What is quantum computing?"      → General AI response
"What time is it?"                → Returns current time
```

## Setup Instructions

### Prerequisites
- Python 3.10+ (recommended: 3.10.10)
- Windows/macOS/Linux
- Microphone (for voice input)
- Speakers (for voice output)

### Step 1: Clone and Navigate
```bash
cd jarvis
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### PyAudio Installation (if issues occur)
**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### Step 4: Install Frontend Dependencies
```bash
cd ../frontend
pip install -r requirements.txt
```

### Step 5: Configure Environment (Optional but Recommended)
```bash
cd ..
cp .env.example .env
# Edit .env and add your API keys
```

**For full chat capabilities, add:**
```
OPENAI_API_KEY=sk-your-api-key-here
```

**For better web search, add:**
```
SERPAPI_KEY=your-serpapi-key
```

### Step 6: Run the Backend
```bash
cd backend
python main.py
```
Backend will start at `ws://localhost:8765`

### Step 7: Run the Frontend (New Terminal)
```bash
cd frontend
python main.py
```

## Usage

1. **Text Input**: Type message in the input box and press Enter or click Send
2. **Voice Input**: Click the microphone button, speak, click again to stop
3. **View Status**: The status indicator shows current state (Idle/Listening/Thinking/Speaking)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PyQt5 Frontend                          │
│  ┌─────────┐  ┌────────────┐  ┌─────────┐  ┌────────────┐  │
│  │ Chat UI │  │ Mic Button │  │ Status  │  │ Audio      │  │
│  │         │  │            │  │ Indicator│  │ Recorder   │  │
│  └─────────┘  └────────────┘  └─────────┘  └────────────┘  │
│                        │                                    │
│                 WebSocket Connection                        │
└────────────────────────│────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                WebSocket Handler                     │   │
│  └──────────────────────│──────────────────────────────┘   │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         ▼               ▼               ▼                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ STT Service│  │Brain Router│  │ TTS Service│           │
│  │ (Whisper)  │  │            │  │ (edge-tts) │           │
│  └────────────┘  └──────┬─────┘  └────────────┘           │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         ▼               ▼               ▼                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ General    │  │ Realtime   │  │ Automation │           │
│  │ Chat (LLM) │  │ Search     │  │ Tools      │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### "Connection error" in frontend
- Ensure backend is running (`python backend/main.py`)
- Check if port 8765 is available

### "STT not available"
- Install faster-whisper: `pip install faster-whisper`
- First run downloads the Whisper model (~150MB for base)

### "TTS not working"
- Install edge-tts: `pip install edge-tts`
- Check speaker/audio output settings

### "PyAudio not found"
- See PyAudio installation section above
- Windows users: try `pipwin install pyaudio`

### "No microphone input"
- Check microphone permissions in system settings
- Verify microphone is selected as default input device

### "Chat responses limited"
- Add `OPENAI_API_KEY` to `.env` for full chat capabilities
- Without API key, uses basic fallback responses

### Web search not working
- DuckDuckGo API is used by default (no key needed)
- For better results, add `SERPAPI_KEY` to `.env`

## Extending JARVIS

### Adding New Automation Commands
Edit `backend/tools/automation.py`:
1. Add pattern to `brain/router.py` automation_patterns
2. Add handler method to `AutomationTools` class

### Adding New Voices
Edit `backend/services/tts_service.py`:
- Add voice names to `VOICES` dict
- Use `TTSService.list_voices()` to see all available voices

### Using Local LLMs (Ollama)
Set in `.env`:
```
OPENAI_API_BASE=http://localhost:11434/v1
CHAT_MODEL=llama2
```

## License
MIT License - Feel free to modify and use as you wish!

## Credits
- Inspired by Marvel's J.A.R.V.I.S
- Built with FastAPI, PyQt5, faster-whisper, and edge-tts
