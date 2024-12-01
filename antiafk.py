import subprocess
import sys
import time
import threading

# Try importing required modules and handle missing ones
def install_and_import(module_name):
    try:
        __import__(module_name)
    except ImportError:
        print(f"Module '{module_name}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
    finally:
        globals()[module_name] = __import__(module_name)

# Install missing modules
required_modules = ["keyboard", "pywin32"]
for module in required_modules:
    install_and_import(module)

import keyboard  # Safe to import now
import win32gui
import win32con

# Timer interval in seconds between each cycle of window interactions
TIMER_INTERVAL = 60  # Default is 60 seconds

# Interaction duration per window (in seconds)
INTERACTION_DURATION = 5  # Stay on each window for 5 seconds

# Key sequence to be executed
# Format: (key, press duration in seconds)
KEY_SEQUENCE = [
    ("space", 0.5),  # Press 'space' for 0.5 seconds
    ("r", 1.0)       # Press 'r' for 1.0 second
]

# Excluded window titles
EXCLUDED_TITLES = ["Account Manager"]  # Avoid "Roblox Account Manager"

# Global variable to signal the script to stop when Escape is pressed
stop_script = False

def listen_for_escape():
    """
    Background thread to listen for the Escape key and terminate the script.
    """
    global stop_script
    keyboard.wait("esc")  # Wait until Escape is pressed
    stop_script = True
    print("Escape key pressed. Terminating script...")

def find_roblox_windows():
    """
    Finds all Roblox game windows by title.
    Returns a list of window handles (HWNDs) for windows matching 'Roblox' and not excluded.
    """
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Roblox" in title and not any(excluded in title for excluded in EXCLUDED_TITLES):
                windows.append(hwnd)
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows

def bring_to_foreground(hwnd):
    """
    Brings the specified window to the foreground and ensures it's active.
    """
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"Error bringing window to the foreground: {e}")

def press_key(key, duration):
    """
    Simulates pressing and holding a key for a specified duration.
    """
    try:
        keyboard.press(key)
        time.sleep(duration)
        keyboard.release(key)
    except Exception as e:
        print(f"Error pressing key '{key}': {e}")

def interact_with_window(hwnd):
    """
    Brings the specified window to the foreground and performs the key sequence.
    """
    try:
        bring_to_foreground(hwnd)
        start_time = time.time()
        while time.time() - start_time < INTERACTION_DURATION:
            for key, duration in KEY_SEQUENCE:
                if stop_script:
                    return
                press_key(key, duration)
    except Exception as e:
        print(f"Error interacting with window: {e}")

def switch_windows_and_press_keys():
    """
    Main function to cycle through Roblox windows, bring each to the foreground,
    and perform the key sequence for the interaction duration.
    """
    global stop_script
    while not stop_script:
        roblox_windows = find_roblox_windows()
        if not roblox_windows:
            print("No Roblox windows found. Retrying in 10 seconds...")
            time.sleep(10)
            continue
        print(f"Found {len(roblox_windows)} Roblox window(s). Interacting...")
        for hwnd in roblox_windows:
            if stop_script:
                return
            interact_with_window(hwnd)
        print(f"Waiting for {TIMER_INTERVAL} seconds before repeating...")
        for _ in range(TIMER_INTERVAL):
            if stop_script:
                return
            time.sleep(1)

if __name__ == "__main__":
    print("Starting the automation script. Press 'Esc' to stop.")
    escape_listener_thread = threading.Thread(target=listen_for_escape, daemon=True)
    escape_listener_thread.start()
    try:
        switch_windows_and_press_keys()
    except KeyboardInterrupt:
        print("Script terminated safely.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Script has exited.")
