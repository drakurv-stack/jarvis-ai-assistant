# J.A.R.V.I.S — AI Assistant

A real-life J.A.R.V.I.S-style AI assistant inspired by Iron Man — featuring voice interaction, task automation, and real-time information retrieval. The repository contains three parts that grew at different stages of the project:

## 📁 Repository Layout

| Directory | Description | Stack |
|-----------|-------------|-------|
| `jarvis/` | **Desktop assistant** — modular AI assistant with voice interaction | Python, FastAPI, PyQt5 |
| `backend/` | **API server** | Bun, Hono, TypeScript |
| `webapp/` | **Web client** | React, TypeScript, Tailwind CSS, Vite |

### `jarvis/` — Python desktop assistant

- **Backend** (`jarvis/backend/`): FastAPI server with WebSocket endpoint
  - `brain/` — decision-making / query classification router
  - `services/` — speech-to-text (faster-whisper), text-to-speech (edge-tts), LLM chat (OpenAI-compatible)
  - `tools/` — system automation (apps, websites, reminders), web search / live info
- **Frontend** (`jarvis/frontend/`): PyQt5 desktop GUI
- Run with `python jarvis/start.py`

### `backend/` — Bun API server

Hono-based API server (see `backend/CLAUDE.md` for the agent workflow).

### `webapp/` — React web client

Vite + React + Tailwind web application (see `webapp/CLAUDE.md`).

## 🚀 Quick Start

```bash
# Desktop assistant (Python)
cd jarvis
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
python start.py

# API server (Bun)
cd backend
bun install
bun run dev

# Web app
cd webapp
npm install
npm run dev
```

## 🔐 Environment Variables

Copy the example file and fill in your own keys — **never commit real secrets**:

```bash
cp .env.example .env
```

## 📄 License

MIT — see [LICENSE](LICENSE).
