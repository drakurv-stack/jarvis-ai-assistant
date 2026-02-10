"""
Status Indicator Widget - Shows JARVIS current state
"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush


class StatusDot(QWidget):
    """Animated status dot"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self._color = QColor("#6b7280")  # Gray default
        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._pulse)
        self._pulse_state = False

    def set_color(self, color: str):
        """Set the dot color"""
        self._color = QColor(color)
        self.update()

    def start_pulsing(self):
        """Start pulsing animation"""
        self._pulse_timer.start(500)

    def stop_pulsing(self):
        """Stop pulsing animation"""
        self._pulse_timer.stop()
        self._pulse_state = False
        self.update()

    def _pulse(self):
        """Pulse animation tick"""
        self._pulse_state = not self._pulse_state
        self.update()

    def paintEvent(self, event):
        """Paint the status dot"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Outer glow when pulsing
        if self._pulse_state:
            glow_color = QColor(self._color)
            glow_color.setAlpha(100)
            painter.setBrush(QBrush(glow_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 12, 12)

        # Main dot
        painter.setBrush(QBrush(self._color))
        painter.setPen(Qt.NoPen)
        size = 8 if self._pulse_state else 10
        offset = (12 - size) // 2
        painter.drawEllipse(offset, offset, size, size)


class StatusIndicator(QWidget):
    """Status indicator showing JARVIS state"""

    STATUS_CONFIG = {
        "idle": {"color": "#22c55e", "text": "Ready", "pulse": False},
        "listening": {"color": "#3b82f6", "text": "Listening...", "pulse": True},
        "thinking": {"color": "#f59e0b", "text": "Thinking...", "pulse": True},
        "speaking": {"color": "#8b5cf6", "text": "Speaking...", "pulse": True},
        "connected": {"color": "#22c55e", "text": "Connected", "pulse": False},
        "disconnected": {"color": "#ef4444", "text": "Disconnected", "pulse": False},
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.set_status("disconnected")

    def _setup_ui(self):
        """Setup the indicator UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        # Status dot
        self.dot = StatusDot()
        layout.addWidget(self.dot)

        # Status text
        self.label = QLabel("Disconnected")
        self.label.setFont(QFont("Segoe UI", 10))
        self.label.setStyleSheet("color: #9ca3af;")
        layout.addWidget(self.label)

        # Container styling
        self.setStyleSheet("""
            StatusIndicator {
                background-color: #16213e;
                border-radius: 15px;
                border: 1px solid #0f3460;
            }
        """)

    def set_status(self, status: str):
        """Set the current status"""
        config = self.STATUS_CONFIG.get(status, self.STATUS_CONFIG["idle"])

        self.dot.set_color(config["color"])
        self.label.setText(config["text"])

        if config["pulse"]:
            self.dot.start_pulsing()
        else:
            self.dot.stop_pulsing()
