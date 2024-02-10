import sys
import subprocess
import os
import glob
import fnmatch
import ctypes
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import subprocess
import pyautogui
import time
import threading
import keyboard
import cv2
import numpy as np
from PIL import Image, ImageGrab

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# List of packages that need to be installed
required_packages = [
    "ttkbootstrap",
    "pyautogui",
    "keyboard",
    "opencv-python",
    "Pillow"  # PIL is part of Pillow
]

for package in required_packages:
    try:
        # Try to import the package, and if it's not found, install it
        __import__(package.split()[0])
    except ImportError:
        install(package)

# Global dictionary to keep track of loaded images
loaded_images = {}

# Load kernel32.dll
k32 = ctypes.windll.kernel32

# Disable file system redirection
wow64 = ctypes.c_long(0)
k32.Wow64DisableWow64FsRedirection(ctypes.byref(wow64))

# Modifed load_image function to handle automatic conversion of any image format to PNG
def load_image(image_path):
    try:
        if not image_path.lower().endswith('.png'):
            with Image.open(image_path) as img:
                png_path = os.path.splitext(image_path)[0] + '.png'
                img.save(png_path, 'PNG')
                print(f"Converted to PNG: {png_path}")
                return png_path
        else:
            return image_path
    except Exception as e:
        print(f"Error processing image '{image_path}': {e}")
        return None

class PetSimulatorAssistant(tk.Tk):

    def load_reference_images(self):
        self.reference_images = {'fruits': {}, 'potions': {}, 'toys': {}}
        categories = ['fruits', 'potions', 'toys']  # Define your categories here
        items = {
            'fruits': ['Apple', 'Orange', 'Banana', 'Pineapple', 'Rainbow'],
            'potions': ['Treasure Hunter', 'Damage', 'Coins', 'Luck', 'Speed', 'Diamonds'],
            'toys': ['Tennis ball', 'Toy Bone', 'Squeeky Toy']
        }
        base_path = 'C:\\Apps\\Automation Stuff\\PS99Companion\\reference_images'  # Define your base path here
        print("Base Path:", base_path)  # Moved this print statement here for correct context

        supported_extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp', '*.bmp', '*.tiff', '*.tif']

        for category in categories:
            for item in items[category]:
                image_name = f"{item}.png"  # Assuming you want to load .png files
                image_path = self.find_and_load_image(image_name, base_path)
                if image_path:
                    self.reference_images[category][item] = image_path
                    self.image_found[item] = True  # Mark the image as found
                else:
                    self.image_found[item] = False  # Image not found
                    print(f"Warning: Image file not found for {item} in category {category}.")

    def find_and_load_image(self, image_name, root_path='C:\\Apps\\Automation Stuff\\PS99Companion\\reference_images'):
        # If the image has already been loaded, return the path
        if image_name in loaded_images:
            return loaded_images[image_name]
        
        # Recursively search for the image in the root path
        for subdir, dirs, files in os.walk(root_path):
            for file in files:
                if file.lower().endswith(('.png', '.webp')) and image_name.lower() in file.lower():
                    image_path = os.path.join(subdir, file)
                    png_path = os.path.splitext(image_path)[0] + '.png'
                    
                    # Convert to PNG if it's a webp file
                    if file.lower().endswith('.webp'):
                        try:
                            with Image.open(image_path) as img:
                                img.save(png_path, 'PNG')
                                print(f"Converted to PNG: {png_path}")
                        except Exception as e:
                            print(f"Error converting image '{image_path}' to PNG: {e}")
                            continue  # Skip to the next file

                    loaded_images[image_name] = png_path
                    return png_path
        
        # If the image was not found
        print(f"Image '{image_name}' not found in {root_path}")
        return None
                    
    def recognize_items(self, category):
        recognized_items = {}
        if hasattr(self, 'reference_images') and category in self.reference_images:
            for item, image_path in self.reference_images[category].items():
                if image_path:
                    # Start with a high confidence level and decrease as needed.
                    # Example: Start with 0.9 and decrease in increments of 0.05.
                    confidence_level = 0.9
                    while confidence_level > 0.3:  # Adjust the lower limit as needed.
                        location = pyautogui.locateOnScreen(image_path, confidence=confidence_level)
                        if location:
                            recognized_items[item] = location
                            break  # If found, break out of the loop.
                        confidence_level -= 0.05  # Decrease confidence level.
        return recognized_items
        

    def check_for_banana(self):
        if not self.image_found.get('Banana', False):
            self.status_label.after(0, lambda: self.update_status('Banana image not loaded', style='danger'))
            return
        recognized_items = self.recognize_items('fruits')
        if 'Banana' in recognized_items:
            self.status_label.after(0, lambda: self.update_status('Banana found!', style='success'))
        else:
            self.status_label.after(0, lambda: self.update_status('No Banana detected', style='info'))

    def perform_actions_based_on_recognition(self, recognized_items):
        # Placeholder for action execution logic based on recognized items
        pass
        
    # Placeholder function to perform actions based on buff recognition
    def perform_buff_actions(self, recognized_buffs):
        # TODO: Implement actions based on recognized buffs
        pass
    def __init__(self):
        super().__init__()
        self.title('Pet Simulator 99 Companion v4 by xXGeminiXx/BeeBrained')
        self.geometry('200x300')  # Window size can be adjusted as needed 600x400 or blank to autosize
        self.monitoring_active = False  
        self.setup_hotkeys()  
        self.image_found = {}  # To keep track of found images
        self.load_reference_images()  # Make sure this is called before starting threads


        # Initialize the user interface.
        self.init_ui()
        self.wm_attributes('-topmost', 1)  # This will make the window stay on top
        self.wm_attributes('-alpha', 0.9)  # Set initial transparency to 90%
        # Transparency slider
        self.transparency_scale = ttk.Scale(self, from_=0.1, to=1.0, value=0.9, command=self.change_transparency)
        self.transparency_scale.pack(pady=5)

        # Apply ttkbootstrap style to this root window
        style = tb.Style(theme='cyborg')
        
    def change_transparency(self, value):
        self.wm_attributes('-alpha', float(value))

    def setup_hotkeys(self):
        # Bind keyboard hotkeys to feature toggles
        # These hotkeys will be global (system-wide)
        keyboard.add_hotkey('ctrl+f1', self.toggle_fishing, suppress=True)
        keyboard.add_hotkey('ctrl+f2', self.toggle_item_recognition, suppress=True)
        keyboard.add_hotkey('ctrl+f3', self.toggle_buff_monitoring, suppress=True)
        keyboard.add_hotkey('ctrl+f4', self.toggle_lucky_blocks, suppress=True)
        # Update the GUI to show the hotkeys or print them to the console
        print("Global Hotkeys Activated")

    def buff_monitoring_loop(self):
        # Call self.after to check for buffs every second (1000 milliseconds)
        if self.monitoring_active:
            self.check_for_buffs()
            self.after(1000, self.buff_monitoring_loop)
            
    def init_ui(self):
        # Initialize user interface components
        feature_frame = ttk.Frame(self)
        feature_frame.pack(padx=10, pady=10, fill='x', expand=True)

        # Initialize variables for each feature
        self.fishing_var = tk.BooleanVar()
        self.item_recognition_var = tk.BooleanVar()
        self.buff_monitor_var = tk.BooleanVar()
        self.lucky_block_var = tk.BooleanVar()

        # Set up checkboxes for each feature with commands to toggle them on and off
        ttk.Checkbutton(feature_frame, text='Fishing Bot', variable=self.fishing_var, 
                        onvalue=True, offvalue=False, command=self.toggle_fishing).pack(anchor='w')
        ttk.Checkbutton(feature_frame, text='Item Recognition', state='disabled', variable=self.item_recognition_var, 
                        onvalue=True, offvalue=False, command=self.toggle_item_recognition).pack(anchor='w')
        ttk.Checkbutton(feature_frame, text='Buff Monitoring', variable=self.buff_monitor_var,
                        onvalue=True, offvalue=False, command=self.toggle_buff_monitoring).pack(anchor='w')
        ttk.Checkbutton(feature_frame, text='Open Lucky Blocks', variable=self.lucky_block_var, 
                        onvalue=True, offvalue=False, command=self.toggle_lucky_blocks).pack(anchor='w')

        # Status label to display the current status of the application
        self.status_label = ttk.Label(self, text='Status: Idle', bootstyle=INFO)
        self.status_label.pack(pady=10)

        # Bind hotkeys for quick access to features
        self.bind_hotkeys()

    def bind_hotkeys(self):
        # Bind keyboard hotkeys to feature toggles
        # Placeholder for actual hotkey implementation
        pass

    def toggle_fishing(self):
    # Toggle the fishing bot feature
        if self.fishing_var.get():
            # Checkbox is checked, start fishing bot
            self.start_fishing()
            self.update_status('Fishing Started', style='info')
        else:
        # Checkbox is unchecked, stop fishing bot
            self.stop_fishing()
            self.update_status('Fishing Stopped', style='danger')
            
    def start_fishing(self):
        # Start the fishing bot process
        try:
            # If calling an external script, consider using subprocess.Popen to allow it to run asynchronously.
            self.fishing_process = subprocess.Popen(['python', 'fishing.py'])
        except Exception as e:
            self.update_status(f'Failed to start fishing: {e}', style=DANGER)

    def stop_fishing(self):
        # Stop the fishing bot process
        try:
            if hasattr(self, 'fishing_process'):
                # If using subprocess.Popen, you can terminate the process.
                self.fishing_process.terminate()
        except Exception as e:
            self.update_status(f'Failed to stop fishing: {e}', style=DANGER)

    def toggle_item_recognition(self):
        # Toggle the item recognition feature
        if self.item_recognition_var.get():
            # Checkbox is checked, start item recognition
            self.start_item_recognition()
        else:
            # Checkbox is unchecked, stop item recognition
            self.stop_item_recognition()

    def start_item_recognition(self):
        # Placeholder for starting item recognition
        # TODO: Implement item recognition startup logic
        pass

    def stop_item_recognition(self):
        # Placeholder for stopping item recognition
        # TODO: Implement item recognition shutdown logic
        pass

    def toggle_buff_monitoring(self):
        if self.buff_monitor_var.get():
            self.monitoring_active = True  # Enable monitoring
            self.start_buff_monitoring()
        else:
            self.monitoring_active = False  # Disable monitoring
            self.stop_buff_monitoring()
            self.update_status('Buff Monitoring Stopped', style='warning')
    
    def stop_buff_monitoring(self):
        # Perform any cleanup if necessary
        # 'self.monitoring_active' is already set to False in 'toggle_buff_monitoring'
        self.update_status('Buff Monitoring Stopped', style='warning')  # Optional based on your design

    def start_buff_monitoring(self):
        self.monitoring_active = True
        threading.Thread(target=self.buff_monitoring_loop, daemon=True).start()

    def stop_buff_monitoring(self):
        self.monitoring_active = False  # This flag will stop the loop in `buff_monitoring_loop`

    def buff_monitoring_loop(self):
        while self.monitoring_active:
            self.check_for_banana()
            time.sleep(1)  # Adjust the sleep time as necessary
    def capture_bottom_left_screen(self):
            screen_width, screen_height = pyautogui.size()
            region = (0, int(screen_height * 0.9), int(screen_width * 0.1), screen_height)  # Adjust to capture bottom left 10%
            screen = np.array(ImageGrab.grab(bbox=region))
            if screen.size == 0:
                print("Error: No screen data captured.")
                return None
            screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
            return screen


    def check_for_buffs(self):
        recognized_buffs = self.recognize_items('buffs')  # Call with one argument
        if recognized_buffs:
            for buff, location in recognized_buffs.items():
                self.status_label.after(0, lambda: self.update_status(f'{buff} found at {location}', style='success'))
        else:
            self.status_label.after(0, lambda: self.update_status('No buffs detected', style='info'))

        # Modify the buff monitoring loop to use the new check_for_buffs method
# Corrected method in PetSimulatorAssistant class
    def buff_monitoring_loop(self):
        while self.monitoring_active:
            self.check_for_buffs()
            time.sleep(1)  # Adjust the sleep time as necessary


    def setup_hotkeys(self):
        keyboard.add_hotkey('ctrl+f1', self.toggle_fishing)
        keyboard.add_hotkey('ctrl+f2', self.toggle_item_recognition)
        keyboard.add_hotkey('ctrl+f3', self.toggle_buff_monitoring)
        keyboard.add_hotkey('ctrl+f4', self.toggle_lucky_blocks)
        # Update the GUI to show the hotkeys or print them to the console
        print("Hotkeys: \n - Ctrl+F1: Fishing\n - Ctrl+F2: Item Recognition\n - Ctrl+F3: Buff Monitoring\n - Ctrl+F4: Lucky Blocks")

    def toggle_lucky_blocks(self):
        # Toggle the lucky blocks opening feature
        if self.lucky_block_var.get():
            # Checkbox is checked, start opening lucky blocks
            self.start_opening_lucky_blocks()
        else:
            # Checkbox is unchecked, stop opening lucky blocks
            self.stop_opening_lucky_blocks()

    def start_opening_lucky_blocks(self):
        # Start the process of opening lucky blocks
        try:
            self.lucky_blocks_process = subprocess.Popen(['python', 'openluckyblocks.py'])
        except Exception as e:
            self.update_status(f'Failed to start lucky blocks: {e}', style=DANGER)

    def stop_opening_lucky_blocks(self):
        # Stop the process of opening lucky blocks
        try:
            if hasattr(self, 'lucky_blocks_process'):
                self.lucky_blocks_process.terminate()
        except Exception as e:
            self.update_status(f'Failed to stop lucky blocks: {e}', style=DANGER)

    def stop_all(self):
        # Stop all running features and update the status label
        self.stop_fishing()
        self.stop_item_recognition()
        self.stop_buff_monitoring()
        self.stop_opening_lucky_blocks()
        self.update_status('Stopped all features', style=DANGER)

    def update_status(self, status_text, style=INFO):
        # Update the status label with provided text and style
        self.status_label.config(text=f'Status: {status_text}', bootstyle=style)

# Main function to run the application
def main():
    app = PetSimulatorAssistant()
    app.mainloop()

# Ensure that this script is the main program and run the application
if __name__ == '__main__':
    # Run the application
    app = PetSimulatorAssistant()
    app.after(1000, app.buff_monitoring_loop)
    app.mainloop()
