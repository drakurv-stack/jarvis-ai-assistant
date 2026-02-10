"""
Main Window - J.A.R.V.I.S Desktop Interface
"""
import asyncio
import base64
import json
import sys
import os
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel,
    QScrollArea, QFrame, QSizePolicy, QApplication
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QSize
)
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

from widgets.chat_bubble import ChatBubble
from widgets.status_indicator import StatusIndicator
from widgets.mic_button import MicButton
from widgets.audio_recorder import AudioRecorder

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.schemas import MessageType, AssistantStatus, WebSocketMessage


# Dark theme stylesheet
DARK_STYLESHEET = """
QMainWindow {
    background-color: #1a1a2e;
}

QWidget {
    background-color: #1a1a2e;
    color: #eaeaea;
}

QLineEdit {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 20px;
    padding: 12px 20px;
    font-size: 14px;
    color: #eaeaea;
}

QLineEdit:focus {
    border-color: #00d4ff;
}

QPushButton {
    background-color: #0f3460;
    border: none;
    border-radius: 20px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: bold;
    color: #eaeaea;
}

QPushButton:hover {
    background-color: #1a4a7a;
}

QPushButton:pressed {
    background-color: #00d4ff;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #16213e;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #0f3460;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00d4ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QLabel {
    color: #eaeaea;
}
"""


class WebSocketThread(QThread):
    """Thread for handling WebSocket communication"""
    message_received = pyqtSignal(str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url: str = "ws://localhost:8765/ws"):
        super().__init__()
        self.url = url
        self.websocket = None
        self._running = False
        self._send_queue = asyncio.Queue()

    def run(self):
        """Run the WebSocket connection in event loop"""
        self._running = True
        asyncio.run(self._run_async())

    async def _run_async(self):
        """Async WebSocket handler"""
        try:
            import websockets

            async with websockets.connect(self.url) as ws:
                self.websocket = ws
                self.connected.emit()

                # Handle both receiving and sending
                receive_task = asyncio.create_task(self._receive_messages())
                send_task = asyncio.create_task(self._send_messages())

                while self._running:
                    done, pending = await asyncio.wait(
                        [receive_task, send_task],
                        return_when=asyncio.FIRST_COMPLETED,
                        timeout=0.1
                    )

                    for task in done:
                        if task == receive_task and self._running:
                            receive_task = asyncio.create_task(self._receive_messages())
                        elif task == send_task and self._running:
                            send_task = asyncio.create_task(self._send_messages())

                for task in [receive_task, send_task]:
                    task.cancel()

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.disconnected.emit()

    async def _receive_messages(self):
        """Receive messages from WebSocket"""
        try:
            message = await self.websocket.recv()
            self.message_received.emit(message)
        except:
            pass

    async def _send_messages(self):
        """Send queued messages"""
        try:
            message = await asyncio.wait_for(self._send_queue.get(), timeout=0.1)
            if self.websocket:
                await self.websocket.send(message)
        except asyncio.TimeoutError:
            pass
        except:
            pass

    def send_message(self, message: str):
        """Queue a message to send"""
        try:
            asyncio.run_coroutine_threadsafe(
                self._send_queue.put(message),
                asyncio.get_event_loop()
            )
        except:
            # If no event loop, create one temporarily
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._send_queue.put(message))

    def stop(self):
        """Stop the WebSocket thread"""
        self._running = False


class MainWindow(QMainWindow):
    """Main JARVIS window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S - AI Assistant")
        self.setMinimumSize(600, 800)
        self.resize(700, 900)

        # Apply dark theme
        self.setStyleSheet(DARK_STYLESHEET)

        # State
        self.current_status = AssistantStatus.IDLE
        self.ws_thread: Optional[WebSocketThread] = None
        self.audio_recorder = AudioRecorder()

        # Setup UI
        self._setup_ui()

        # Connect to backend
        self._connect_to_backend()

    def _setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header with title and status
        header = self._create_header()
        layout.addWidget(header)

        # Chat area
        chat_area = self._create_chat_area()
        layout.addWidget(chat_area, 1)

        # Input area
        input_area = self._create_input_area()
        layout.addWidget(input_area)

    def _create_header(self) -> QWidget:
        """Create header with title and status indicator"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("J.A.R.V.I.S")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        layout.addWidget(title)

        layout.addStretch()

        # Status indicator
        self.status_indicator = StatusIndicator()
        layout.addWidget(self.status_indicator)

        return header

    def _create_chat_area(self) -> QWidget:
        """Create scrollable chat area"""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Chat container
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(5, 5, 5, 5)

        scroll.setWidget(self.chat_container)
        self.chat_scroll = scroll

        # Welcome message
        self._add_assistant_message(
            "Hello! I'm J.A.R.V.I.S, your AI assistant. "
            "How can I help you today? You can type a message or click the microphone to speak."
        )

        return scroll

    def _create_input_area(self) -> QWidget:
        """Create input area with text field and buttons"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Text input
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type a message or click the mic to speak...")
        self.text_input.returnPressed.connect(self._on_send_text)
        layout.addWidget(self.text_input, 1)

        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._on_send_text)
        self.send_btn.setFixedWidth(80)
        layout.addWidget(self.send_btn)

        # Mic button
        self.mic_btn = MicButton()
        self.mic_btn.clicked.connect(self._on_mic_click)
        layout.addWidget(self.mic_btn)

        return container

    def _connect_to_backend(self):
        """Connect to the backend WebSocket server"""
        self.ws_thread = WebSocketThread()
        self.ws_thread.message_received.connect(self._on_message_received)
        self.ws_thread.connected.connect(self._on_connected)
        self.ws_thread.disconnected.connect(self._on_disconnected)
        self.ws_thread.error.connect(self._on_ws_error)
        self.ws_thread.start()

    def _on_connected(self):
        """Handle WebSocket connection"""
        self.status_indicator.set_status("connected")
        print("Connected to JARVIS backend")

    def _on_disconnected(self):
        """Handle WebSocket disconnection"""
        self.status_indicator.set_status("disconnected")
        print("Disconnected from JARVIS backend")

    def _on_ws_error(self, error: str):
        """Handle WebSocket error"""
        print(f"WebSocket error: {error}")
        self._add_assistant_message(
            f"Connection error: {error}. Make sure the backend server is running."
        )

    def _on_message_received(self, raw_message: str):
        """Handle received WebSocket message"""
        try:
            message = WebSocketMessage.from_json(raw_message)

            if message.type == MessageType.STATUS_UPDATE:
                self._update_status(message.status)

            elif message.type == MessageType.TRANSCRIPTION:
                # Show what was heard
                self._add_user_message(message.data)

            elif message.type == MessageType.RESPONSE:
                # Show assistant response
                response_data = message.data
                text = response_data.get("text", str(response_data))
                self._add_assistant_message(text)

            elif message.type == MessageType.AUDIO_RESPONSE:
                # Play audio response
                self._play_audio(message.data)

            elif message.type == MessageType.ERROR:
                self._add_assistant_message(f"Error: {message.data}")

        except Exception as e:
            print(f"Error processing message: {e}")

    def _update_status(self, status: AssistantStatus):
        """Update the status indicator"""
        self.current_status = status
        self.status_indicator.set_status(status.value)

        # Update mic button state
        if status == AssistantStatus.LISTENING:
            self.mic_btn.set_recording(True)
        else:
            self.mic_btn.set_recording(False)

    def _on_send_text(self):
        """Handle sending text message"""
        text = self.text_input.text().strip()
        if not text:
            return

        # Show user message
        self._add_user_message(text)

        # Clear input
        self.text_input.clear()

        # Send to backend
        message = WebSocketMessage(
            type=MessageType.TEXT_INPUT,
            data=text
        )
        self._send_message(message)

    def _on_mic_click(self):
        """Handle microphone button click"""
        if self.audio_recorder.is_recording:
            # Stop recording
            audio_data = self.audio_recorder.stop_recording()
            self.mic_btn.set_recording(False)

            if audio_data:
                # Encode and send to backend
                audio_b64 = base64.b64encode(audio_data).decode("utf-8")
                message = WebSocketMessage(
                    type=MessageType.AUDIO_INPUT,
                    data=audio_b64
                )
                self._send_message(message)
        else:
            # Start recording
            self.audio_recorder.start_recording()
            self.mic_btn.set_recording(True)

    def _send_message(self, message: WebSocketMessage):
        """Send message to backend"""
        if self.ws_thread:
            # Run in the WS thread's event loop
            import threading
            def send():
                try:
                    import websockets
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self._async_send(message.to_json()))
                except Exception as e:
                    print(f"Send error: {e}")

            threading.Thread(target=send, daemon=True).start()

    async def _async_send(self, message: str):
        """Async send helper"""
        try:
            import websockets
            async with websockets.connect("ws://localhost:8765/ws") as ws:
                await ws.send(message)
                # Wait for responses
                while True:
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=30)
                        self._on_message_received(response)
                        msg = WebSocketMessage.from_json(response)
                        if msg.status == AssistantStatus.IDLE:
                            break
                    except asyncio.TimeoutError:
                        break
        except Exception as e:
            self._on_ws_error(str(e))

    def _add_user_message(self, text: str):
        """Add a user message bubble"""
        bubble = ChatBubble(text, is_user=True)
        self.chat_layout.addWidget(bubble)
        self._scroll_to_bottom()

    def _add_assistant_message(self, text: str):
        """Add an assistant message bubble"""
        bubble = ChatBubble(text, is_user=False)
        self.chat_layout.addWidget(bubble)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """Scroll chat to bottom"""
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))

    def _play_audio(self, audio_b64: str):
        """Play audio response"""
        try:
            import tempfile
            from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
            from PyQt5.QtCore import QUrl

            # Decode and save to temp file
            audio_data = base64.b64decode(audio_b64)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name

            # Play audio
            if not hasattr(self, 'media_player'):
                self.media_player = QMediaPlayer()

            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(temp_path)))
            self.media_player.play()

        except Exception as e:
            print(f"Audio playback error: {e}")

    def closeEvent(self, event):
        """Handle window close"""
        if self.ws_thread:
            self.ws_thread.stop()
            self.ws_thread.wait(1000)

        if self.audio_recorder.is_recording:
            self.audio_recorder.stop_recording()

        event.accept()
