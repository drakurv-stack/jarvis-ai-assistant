"""
FastAPI Backend Server for J.A.R.V.I.S
Handles WebSocket connections, speech processing, and AI responses
"""
import asyncio
import base64
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.schemas import (
    MessageType,
    AssistantStatus,
    WebSocketMessage,
    QueryType
)

from brain.router import BrainRouter
from services.stt_service import STTService
from services.tts_service import TTSService
from services.chat_service import ChatService
from tools.automation import AutomationTools
from tools.realtime import RealtimeTools

app = FastAPI(title="J.A.R.V.I.S Backend", version="1.0.0")

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
stt_service: Optional[STTService] = None
tts_service: Optional[TTSService] = None
brain_router: Optional[BrainRouter] = None
chat_service: Optional[ChatService] = None
automation_tools: Optional[AutomationTools] = None
realtime_tools: Optional[RealtimeTools] = None


@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    global stt_service, tts_service, brain_router, chat_service, automation_tools, realtime_tools

    print("🚀 Initializing J.A.R.V.I.S services...")

    stt_service = STTService()
    tts_service = TTSService()
    brain_router = BrainRouter()
    chat_service = ChatService()
    automation_tools = AutomationTools()
    realtime_tools = RealtimeTools()

    print("✅ All services initialized!")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "J.A.R.V.I.S"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication"""
    await websocket.accept()
    print("🔌 Client connected")

    async def send_status(status: AssistantStatus):
        """Send status update to client"""
        msg = WebSocketMessage(
            type=MessageType.STATUS_UPDATE,
            status=status
        )
        await websocket.send_text(msg.to_json())

    async def send_message(msg_type: MessageType, data: any):
        """Send message to client"""
        msg = WebSocketMessage(type=msg_type, data=data)
        await websocket.send_text(msg.to_json())

    try:
        # Send initial idle status
        await send_status(AssistantStatus.IDLE)

        while True:
            # Receive message from client
            raw_data = await websocket.receive_text()
            message = WebSocketMessage.from_json(raw_data)

            if message.type == MessageType.CANCEL:
                await send_status(AssistantStatus.IDLE)
                continue

            user_text = ""

            # Handle audio input
            if message.type == MessageType.AUDIO_INPUT:
                await send_status(AssistantStatus.LISTENING)

                # Decode base64 audio
                audio_bytes = base64.b64decode(message.data)

                # Save to temp file for processing
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(audio_bytes)
                    temp_path = f.name

                await send_status(AssistantStatus.THINKING)

                # Transcribe audio
                user_text = await stt_service.transcribe(temp_path)
                os.unlink(temp_path)  # Clean up temp file

                # Send transcription to client
                await send_message(MessageType.TRANSCRIPTION, user_text)

            # Handle text input
            elif message.type == MessageType.TEXT_INPUT:
                await send_status(AssistantStatus.THINKING)
                user_text = message.data

            if not user_text or not user_text.strip():
                await send_message(MessageType.ERROR, "No input received")
                await send_status(AssistantStatus.IDLE)
                continue

            # Route through brain to determine query type
            decision = await brain_router.route(user_text)

            # Process based on query type
            response_text = ""

            if decision.query_type == QueryType.GENERAL_QUERY:
                response_text = await chat_service.get_response(user_text)

            elif decision.query_type == QueryType.REALTIME_QUERY:
                # Get web search results and summarize
                search_results = await realtime_tools.web_search(user_text)
                response_text = await chat_service.summarize_search(user_text, search_results)

            elif decision.query_type == QueryType.AUTOMATION_QUERY:
                # Execute automation task
                result = await automation_tools.execute(decision.intent, decision.parameters)
                response_text = result

            # Send text response
            await send_message(MessageType.RESPONSE, {
                "text": response_text,
                "query_type": decision.query_type.value,
                "intent": decision.intent
            })

            # Generate and send audio response
            await send_status(AssistantStatus.SPEAKING)
            audio_data = await tts_service.synthesize(response_text)

            if audio_data:
                audio_b64 = base64.b64encode(audio_data).decode("utf-8")
                await send_message(MessageType.AUDIO_RESPONSE, audio_b64)

            # Return to idle
            await send_status(AssistantStatus.IDLE)

    except WebSocketDisconnect:
        print("🔌 Client disconnected")
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            await send_message(MessageType.ERROR, str(e))
            await send_status(AssistantStatus.IDLE)
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
