import subprocess
import sys
import time
import threading
import keyboard
import win32gui
import win32con
from pkg_resources import WorkingSet, DistributionNotFound

# ========== Install Required Modules ==========
def install_module(package):
    """
    Installs a Python module if not already installed.
    Args:
        package: The name of the package to install.
    """
    try:
        # Check if the module is already installed
        ws = WorkingSet()
        ws.require(package)  # Check if the package exists
    except DistributionNotFound:
        print(f"Module '{package}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        print(f"Error checking/installing module '{package}': {e}")


# List of required modules
required_modules = ['pywin32', 'keyboard']

# Check and install each module
for module in required_modules:
    install_module(module)

# ========== Script Logic ==========
# Timer interval in seconds between each cycle of window interactions
TIMER_INTERVAL = 60  # Default is 60 seconds

# Interaction duration per window (in seconds)
INTERACTION_DURATION = 5  # Stay on each window for 5 seconds

# Key sequence to be executed
# Format: (key, press duration in seconds)
KEY_SEQUENCE = [
    ('space', 0.5),  # Press 'space' for 0.5 seconds
    ('r', 1.0)       # Press 'r' for 1.0 second
]

# Excluded window titles
EXCLUDED_TITLES = ['Account Manager']  # Avoid "Roblox Account Manager"

# Global variable to signal the script to stop when Escape is pressed
stop_script = False


def listen_for_escape():
    """
    Background thread to listen for the Escape key and terminate the script.
    """
    global stop_script
    keyboard.wait('esc')  # Wait until Escape is pressed
    stop_script = True
    print("Escape key pressed. Terminating script...")
    sys.exit(0)  # Terminate the script immediately


def find_roblox_windows():
    """
    Finds all Roblox game windows by title.
    Returns a list of window handles (HWNDs) for windows matching 'Roblox' and not excluded.
    """
    def enum_windows_callback(hwnd, windows):
        # Check if the window is visible
        if win32gui.IsWindowVisible(hwnd):
            # Get the window title
            title = win32gui.GetWindowText(hwnd)
            # Include only windows with 'Roblox' in the title and not excluded
            if 'Roblox' in title and not any(excluded in title for excluded in EXCLUDED_TITLES):
                windows.append(hwnd)

    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)  # Enumerate all windows
    return windows


def bring_to_foreground(hwnd):
    """
    Brings the specified window to the foreground and ensures it's active.
    Args:
        hwnd: Handle to the window to be brought to the foreground.
    """
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restore if minimized
        win32gui.SetForegroundWindow(hwnd)  # Bring to foreground
        print(f"Brought window '{win32gui.GetWindowText(hwnd)}' to the foreground.")
    except Exception as e:
        print(f"Error bringing window to the foreground: {e}")


def press_key(key, duration):
    """
    Simulates pressing and holding a key for a specified duration.
    Args:
        key: The key to press (e.g., 'space', 'r').
        duration: How long to hold the key down, in seconds.
    """
    try:
        keyboard.press(key)  # Press the key
        time.sleep(duration)  # Hold for the specified duration
        keyboard.release(key)  # Release the key
    except Exception as e:
        print(f"Error pressing key '{key}': {e}")


def interact_with_window(hwnd):
    """
    Brings the specified window to the foreground and performs the key sequence.
    Args:
        hwnd: Handle to the window to interact with.
    """
    try:
        bring_to_foreground(hwnd)  # Bring the window to the foreground

        # Perform the key sequence for the configured duration
        start_time = time.time()
        while time.time() - start_time < INTERACTION_DURATION:
            for key, duration in KEY_SEQUENCE:
                if stop_script:  # Stop the script if needed
                    return
                press_key(key, duration)  # Perform the key press
    except Exception as e:
        print(f"Error interacting with window: {e}")


def switch_windows_and_press_keys():
    """
    Main function to cycle through Roblox windows, bring each to the foreground,
    and perform the key sequence for the interaction duration.
    """
    global stop_script

    while not stop_script:
        roblox_windows = find_roblox_windows()  # Find all Roblox windows
        if not roblox_windows:
            print("No Roblox windows found. Retrying in 10 seconds...")
            time.sleep(10)  # Wait before retrying
            continue

        print(f"Found {len(roblox_windows)} Roblox window(s). Interacting...")

        # Interact with each window once per cycle
        for hwnd in roblox_windows:
            if stop_script:  # Exit if the script is stopped
                return
            interact_with_window(hwnd)  # Interact with the window

        # Wait for the configured interval before the next cycle
        print(f"Waiting for {TIMER_INTERVAL} seconds before repeating...")
        for _ in range(TIMER_INTERVAL):
            if stop_script:  # Stop the script during the wait
                return
            time.sleep(1)  # Sleep in small increments for responsiveness


if __name__ == "__main__":
    print("Starting the automation script. Press 'Esc' to stop.")

    # Start the Escape key listener in a separate thread
    escape_listener_thread = threading.Thread(target=listen_for_escape, daemon=True)
    escape_listener_thread.start()

    try:
        switch_windows_and_press_keys()  # Start the main loop
    except SystemExit:
        print("Script terminated safely.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Script has exited.")
