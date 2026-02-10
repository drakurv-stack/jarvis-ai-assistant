"""
Chat Bubble Widget - Displays messages in chat format
"""
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ChatBubble(QFrame):
    """Chat message bubble widget"""

    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self._setup_ui(text)

    def _setup_ui(self, text: str):
        """Setup the bubble UI"""
        # Outer layout for alignment
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 5, 0, 5)

        if self.is_user:
            outer_layout.addStretch()

        # Message bubble
        bubble = QFrame()
        bubble.setMaximumWidth(450)

        if self.is_user:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #00d4ff;
                    border-radius: 15px;
                    padding: 12px 16px;
                }
                QLabel {
                    color: #1a1a2e;
                    background-color: transparent;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: #16213e;
                    border-radius: 15px;
                    padding: 12px 16px;
                    border: 1px solid #0f3460;
                }
                QLabel {
                    color: #eaeaea;
                    background-color: transparent;
                }
            """)

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        # Sender label
        sender = QLabel("You" if self.is_user else "J.A.R.V.I.S")
        sender.setFont(QFont("Segoe UI", 9, QFont.Bold))
        if not self.is_user:
            sender.setStyleSheet("color: #00d4ff; background-color: transparent;")
        bubble_layout.addWidget(sender)

        # Message text
        message = QLabel(text)
        message.setWordWrap(True)
        message.setFont(QFont("Segoe UI", 11))
        message.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble_layout.addWidget(message)

        outer_layout.addWidget(bubble)

        if not self.is_user:
            outer_layout.addStretch()
