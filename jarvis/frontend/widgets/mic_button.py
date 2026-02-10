"""
Microphone Button Widget - Push-to-talk button with visual feedback
"""
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush


class MicButton(QPushButton):
    """Microphone button with visual recording state"""

    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_recording = False
        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_value = 0
        self._pulse_direction = 1

        self._setup_ui()

    def _setup_ui(self):
        """Setup button appearance"""
        self.setFixedSize(60, 60)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Click to record voice (click again to stop)")
        self._update_style()

    def _update_style(self):
        """Update button style based on state"""
        if self._is_recording:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    border: 3px solid #dc2626;
                    border-radius: 30px;
                    font-size: 24px;
                }
                QPushButton:hover {
                    background-color: #f87171;
                }
            """)
            self.setText("⬛")  # Stop icon
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0f3460;
                    border: 3px solid #00d4ff;
                    border-radius: 30px;
                    font-size: 24px;
                }
                QPushButton:hover {
                    background-color: #1a4a7a;
                    border-color: #00ffff;
                }
                QPushButton:pressed {
                    background-color: #00d4ff;
                }
            """)
            self.setText("🎤")  # Mic icon

    def set_recording(self, is_recording: bool):
        """Set the recording state"""
        self._is_recording = is_recording
        self._update_style()

        if is_recording:
            self._pulse_timer.start(50)
            self.recording_started.emit()
        else:
            self._pulse_timer.stop()
            self.recording_stopped.emit()

    @property
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self._is_recording

    def _update_pulse(self):
        """Update pulse animation"""
        self._pulse_value += self._pulse_direction * 5
        if self._pulse_value >= 100:
            self._pulse_direction = -1
        elif self._pulse_value <= 0:
            self._pulse_direction = 1
        self.update()

    def paintEvent(self, event):
        """Custom paint for pulse effect during recording"""
        super().paintEvent(event)

        if self._is_recording:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            # Draw pulsing ring
            alpha = int(100 - self._pulse_value)
            color = QColor(239, 68, 68, alpha)
            pen = QPen(color)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            size = 30 + (self._pulse_value * 0.15)
            offset = (60 - size) / 2
            painter.drawEllipse(int(offset), int(offset), int(size), int(size))
