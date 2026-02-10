"""
Shared schemas/messages between frontend and backend
"""
from enum import Enum
from typing import Optional, Any
from dataclasses import dataclass, asdict
import json


class MessageType(str, Enum):
    # Client -> Server
    AUDIO_INPUT = "audio_input"
    TEXT_INPUT = "text_input"
    CANCEL = "cancel"

    # Server -> Client
    STATUS_UPDATE = "status_update"
    TRANSCRIPTION = "transcription"
    RESPONSE = "response"
    AUDIO_RESPONSE = "audio_response"
    ERROR = "error"


class AssistantStatus(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"


class QueryType(str, Enum):
    GENERAL_QUERY = "general_query"
    REALTIME_QUERY = "realtime_query"
    AUTOMATION_QUERY = "automation_query"


@dataclass
class WebSocketMessage:
    type: MessageType
    data: Any = None
    status: Optional[AssistantStatus] = None

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value if isinstance(self.type, Enum) else self.type,
            "data": self.data,
            "status": self.status.value if self.status else None
        })

    @classmethod
    def from_json(cls, json_str: str) -> "WebSocketMessage":
        data = json.loads(json_str)
        return cls(
            type=MessageType(data["type"]),
            data=data.get("data"),
            status=AssistantStatus(data["status"]) if data.get("status") else None
        )


@dataclass
class BrainDecision:
    query_type: QueryType
    intent: str
    parameters: dict
    confidence: float

    def to_dict(self) -> dict:
        return {
            "query_type": self.query_type.value,
            "intent": self.intent,
            "parameters": self.parameters,
            "confidence": self.confidence
        }
