import pyautogui
import time
import keyboard
import keyboard

# Simulate pressing 'F'
# CONSTANTS
PAUSE_KEY = "p"  # Key to pause execution
WAIT_BEFORE_CLICK = 2  # Wait time in seconds before clicking
WAIT_AFTER_CLICK = 3  # Wait time in seconds after clicking

def click():
    """Simulates a mouse click."""
    pyautogui.click()

def main_loop():
    """Main loop to open 'lucky block' buffs."""
    while True:
        # Check if PAUSE_KEY is pressed to pause execution
        if keyboard.is_pressed(PAUSE_KEY):
            print("Execution paused by the user. Press any key to exit.")
            break

        # Hit 'F', wait 2 seconds, click, and then wait for 30 seconds
        time.sleep(WAIT_BEFORE_CLICK)  # Wait before click
        keyboard.press('f')
        keyboard.release('f')
        time.sleep(WAIT_BEFORE_CLICK)  # Wait before click
        click()  # Simulate click
        time.sleep(WAIT_AFTER_CLICK)  # Wait after click

if __name__ == "__main__":
    main_loop()
