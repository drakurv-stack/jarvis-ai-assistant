#!/usr/bin/env python3
"""
Quick start script for J.A.R.V.I.S
Run this from the jarvis root directory
"""
import subprocess
import sys
import os
import time


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ is required")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")


def install_dependencies():
    """Install all dependencies"""
    print("\n📦 Installing backend dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], check=True)

    print("\n📦 Installing frontend dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "frontend/requirements.txt"], check=True)


def main():
    """Main setup and run"""
    print("=" * 50)
    print("🤖 J.A.R.V.I.S Setup & Launch")
    print("=" * 50)

    check_python_version()

    # Check if we need to install
    try:
        import fastapi
        import PyQt5
        print("✅ Dependencies already installed")
    except ImportError:
        print("\n⚙️  First time setup - installing dependencies...")
        install_dependencies()

    print("\n🚀 Starting J.A.R.V.I.S...")
    print("-" * 50)

    # Start backend in background
    print("Starting backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, "backend/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    # Wait for backend to start
    time.sleep(3)

    # Start frontend
    print("Starting frontend...")
    try:
        subprocess.run([sys.executable, "frontend/main.py"], check=True)
    except KeyboardInterrupt:
        pass
    finally:
        backend_process.terminate()
        print("\n👋 J.A.R.V.I.S shutdown complete")


if __name__ == "__main__":
    main()
