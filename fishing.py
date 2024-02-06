from pyautogui import locateOnScreen, pixel
import win32api, win32con
import time
import keyboard

# CONSTANTS

CPS = 45  # Clicks per second
LOOP_THRESHOLD = 30  # Loop executes 30 times per second
IMG = 'C:\\Apps\\PS99-Fish-Macro-main\\TAP.png'  # Path to image file
CONFIDENCE = 0.5  # Confidence level for image recognition
WHITE = (255, 255, 255)  # RGB value for white
DEBUGGING = False  # Debug mode flag
STOP_KEY = "p"  # Key to stop execution
# Calculated CONSTANTS
CPS_DELAY = 1 / CPS  # Delay between clicks based on CPS
LOOP_THRESHOLD_DELAY = 1 / LOOP_THRESHOLD  # Delay for each loop iteration

# Functions

def Clickl(x=None, y=None):
    """Simulates a mouse click at the specified coordinates."""
    # Move cursor to specified position if coordinates are given
    if x is not None and y is not None:
        win32api.SetCursorPos((x, y))

    # Simulate mouse click
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def Find_IMG(img=IMG):
    """Attempts to find an image on the screen."""
    try:
        locateOnScreen(IMG, confidence=CONFIDENCE)
        return 0  # Image found
    except Exception as e:
        return -1  # Image not found

def Check_For_White_Pixel(x=None, y=None):
    """Checks if the pixel at given coordinates is white."""
    if x is None or y is None:
        print("Not specified coordinates")
        return -2  # Coordinates not specified
    
    # Check if pixel color matches white
    if pixel(x, y) == WHITE:
        return 0  # White pixel found
    else:
        return -1  # White pixel not found

def Fish():
    """Handles the fishing action."""
    # Stop execution if STOP_KEY is pressed
    if keyboard.is_pressed(STOP_KEY):
        print("Code execution stopped by the user.")
        return
    if DEBUGGING:
        return
    # Delays and clicks for fishing action
    time.sleep(2)  # Delay before first click/after minigame
    Clickl()       # First click (throw bobber/line)
    time.sleep(4.5)  # Increased delay before second click (retrieve fish)
    Clickl()       # Second click (begin minigame)
    time.sleep(0.5)  # Additional delay

def ClickWhileBober():
    """Clicks while a white pixel is detected at specific coordinates."""
    # Stop execution if STOP_KEY is pressed
    if keyboard.is_pressed(STOP_KEY):
        print("Code execution stopped by the user.")
        return
    # Keep clicking as long as white pixel is detected
    while Check_For_White_Pixel(1492, 234) == 0:
        Clickl()
        time.sleep(CPS_DELAY)
        # Stop if STOP_KEY is pressed during loop
        if keyboard.is_pressed(STOP_KEY):
            print("Code execution stopped by the user.")
            break

# Main loop
while True:
    # Stop execution if STOP_KEY is pressed
    if keyboard.is_pressed(STOP_KEY):
        print("Code execution stopped by the user.")
        break
    time.sleep(LOOP_THRESHOLD_DELAY)  # Loop iteration delay
    # Check for white pixel and image presence
    white_res = Check_For_White_Pixel(1492, 234)
    tap_png_res = Find_IMG(IMG)
    print(f"w {white_res}\nt {tap_png_res}")
    # Determine action based on conditions
    if white_res == 0 and tap_png_res == 0 and not DEBUGGING:
        ClickWhileBober()
    else:
        Fish()
