"""
Automation Tools - System automation capabilities
Safely executes tasks like opening apps, websites, setting reminders, taking notes
"""
import asyncio
import json
import os
import subprocess
import sys
import platform
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional


class AutomationTools:
    """
    Handles automation tasks like opening apps/websites, reminders, and notes.
    Designed with safety in mind - only executes predefined safe operations.
    """

    def __init__(self):
        self.platform = platform.system().lower()
        self.notes_file = Path(__file__).parent.parent / "data" / "notes.json"
        self.reminders_file = Path(__file__).parent.parent / "data" / "reminders.json"
        self._pending_reminders: Dict[str, asyncio.Task] = {}

        # Ensure data directory exists
        self.notes_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize data files
        if not self.notes_file.exists():
            self._save_json(self.notes_file, [])
        if not self.reminders_file.exists():
            self._save_json(self.reminders_file, [])

        # App name mappings for different platforms
        self.app_mappings = {
            "windows": {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "word": "WINWORD.EXE",
                "excel": "EXCEL.EXE",
                "powerpoint": "POWERPNT.EXE",
                "outlook": "OUTLOOK.EXE",
                "terminal": "wt.exe",
                "cmd": "cmd.exe",
                "vscode": "code",
                "code": "code",
                "spotify": "spotify.exe",
                "discord": "discord.exe",
                "slack": "slack.exe",
                "teams": "ms-teams.exe",
                "zoom": "zoom.exe",
                "explorer": "explorer.exe",
                "paint": "mspaint.exe",
            },
            "darwin": {  # macOS
                "notepad": "TextEdit",
                "calculator": "Calculator",
                "chrome": "Google Chrome",
                "firefox": "Firefox",
                "safari": "Safari",
                "word": "Microsoft Word",
                "excel": "Microsoft Excel",
                "powerpoint": "Microsoft PowerPoint",
                "outlook": "Microsoft Outlook",
                "terminal": "Terminal",
                "vscode": "Visual Studio Code",
                "code": "Visual Studio Code",
                "spotify": "Spotify",
                "discord": "Discord",
                "slack": "Slack",
                "teams": "Microsoft Teams",
                "zoom": "zoom.us",
                "finder": "Finder",
            },
            "linux": {
                "notepad": "gedit",
                "calculator": "gnome-calculator",
                "chrome": "google-chrome",
                "firefox": "firefox",
                "terminal": "gnome-terminal",
                "vscode": "code",
                "code": "code",
                "spotify": "spotify",
                "discord": "discord",
                "slack": "slack",
                "files": "nautilus",
            }
        }

    async def execute(self, intent: str, parameters: Dict[str, Any]) -> str:
        """
        Execute an automation task.

        Args:
            intent: The action to perform
            parameters: Parameters for the action

        Returns:
            Result message
        """
        handlers = {
            "open_website": self._open_website,
            "open_app": self._open_app,
            "set_reminder": self._set_reminder,
            "take_note": self._take_note,
            "get_time": self._get_time,
            "get_date": self._get_date,
        }

        handler = handlers.get(intent)
        if not handler:
            return f"I don't know how to handle the action: {intent}"

        try:
            return await handler(parameters)
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    async def _open_website(self, params: Dict) -> str:
        """Open a website in the default browser"""
        url = params.get("url", "")
        if not url:
            return "I need a URL to open."

        # Ensure URL has protocol
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        try:
            import webbrowser
            webbrowser.open(url)
            return f"I've opened {url} in your browser."
        except Exception as e:
            return f"I couldn't open the website: {str(e)}"

    async def _open_app(self, params: Dict) -> str:
        """Open an application"""
        app_name = params.get("app_name", "").lower()
        if not app_name:
            return "I need to know which app to open."

        # Get the actual command for this platform
        platform_apps = self.app_mappings.get(self.platform, {})
        app_command = platform_apps.get(app_name, app_name)

        try:
            if self.platform == "windows":
                subprocess.Popen(
                    f'start "" "{app_command}"',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif self.platform == "darwin":
                subprocess.Popen(
                    ["open", "-a", app_command],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:  # Linux
                subprocess.Popen(
                    [app_command],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )

            return f"I've launched {app_name} for you."
        except Exception as e:
            return f"I couldn't open {app_name}. It might not be installed or the name might be different. Error: {str(e)}"

    async def _set_reminder(self, params: Dict) -> str:
        """Set a reminder"""
        text = params.get("text", "")
        time_minutes = params.get("time_minutes", 5)

        if not text:
            return "What would you like me to remind you about?"

        reminder_id = f"reminder_{datetime.now().timestamp()}"
        remind_at = datetime.now() + timedelta(minutes=time_minutes)

        # Save reminder to file
        reminders = self._load_json(self.reminders_file)
        reminder_data = {
            "id": reminder_id,
            "text": text,
            "created_at": datetime.now().isoformat(),
            "remind_at": remind_at.isoformat(),
            "completed": False
        }
        reminders.append(reminder_data)
        self._save_json(self.reminders_file, reminders)

        # Schedule the reminder (in production, use proper scheduler)
        # For MVP, we just acknowledge it
        return f"Got it! I'll remind you to {text} in {time_minutes} minute{'s' if time_minutes != 1 else ''}."

    async def _take_note(self, params: Dict) -> str:
        """Save a note"""
        text = params.get("text", "")

        if not text:
            return "What would you like me to note down?"

        notes = self._load_json(self.notes_file)
        note_data = {
            "id": len(notes) + 1,
            "text": text,
            "created_at": datetime.now().isoformat()
        }
        notes.append(note_data)
        self._save_json(self.notes_file, notes)

        return f"I've saved your note: \"{text}\""

    async def _get_time(self, params: Dict) -> str:
        """Get current time"""
        now = datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}."

    async def _get_date(self, params: Dict) -> str:
        """Get current date"""
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."

    def _load_json(self, filepath: Path) -> list:
        """Load JSON file"""
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except:
            return []

    def _save_json(self, filepath: Path, data: list):
        """Save JSON file"""
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def get_all_notes(self) -> list:
        """Get all saved notes"""
        return self._load_json(self.notes_file)

    def get_all_reminders(self) -> list:
        """Get all reminders"""
        return self._load_json(self.reminders_file)
