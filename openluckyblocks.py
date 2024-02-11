import pyautogui
import time
import keyboard
import random

# Adjustable variables
PAUSE_KEY = "p"  # Key to pause execution
CLICK_MIN_DELAY = 0.5  # Minimum delay between clicks, in seconds
CLICK_MAX_DELAY = 1.5  # Maximum delay between clicks, in seconds
MOVEMENT_INTERVAL = 240  # Interval for movement simulation, in seconds (4 minutes)
WAIT_BEFORE_CLICK = 2  # Wait time in seconds before clicking
WAIT_AFTER_CLICK = 8.5  # Wait time in seconds after clicking

def click():
    delay = random.uniform(CLICK_MIN_DELAY, CLICK_MAX_DELAY)
    time.sleep(delay)  # Variable delay before click
    pyautogui.click()

def simulate_movement():
    keyboard.press_and_release('w')
    time.sleep(0.5)  # Simulates a short press
    keyboard.press_and_release('s')
    time.sleep(0.5)
    keyboard.press_and_release('a')
    time.sleep(0.5)
    keyboard.press_and_release('d')
    time.sleep(0.5)

def main_loop():
    """Main loop to open 'lucky block' buffs."""
    last_movement_time = time.time()
    
    while True:
        # Check if PAUSE_KEY is pressed to pause execution
        if keyboard.is_pressed(PAUSE_KEY):
            print("Paused. Press any key to continue...")
            keyboard.wait(PAUSE_KEY, True)  # Wait for PAUSE_KEY release and press again to continue
            last_movement_time = time.time()  # Reset movement timer after pause
        
        # Simulate pressing 'F' to open inventory
        keyboard.press_and_release('f')
        time.sleep(WAIT_BEFORE_CLICK)  # Wait before click
        
        click()  # Click to open the lucky block
        
        time.sleep(WAIT_AFTER_CLICK)  # Wait after click
        
        current_time = time.time()
        if current_time - last_movement_time >= MOVEMENT_INTERVAL:
            simulate_movement()  # Simulate movement every 4 minutes
            last_movement_time = current_time

if __name__ == "__main__":
    main_loop()
