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
from PIL import ImageGrab

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
    fruit_color_ranges = {
        'banana': ([25, 150, 50], [32, 255, 255]), # Example HSV lower and upper bounds
        'apple': ([0, 150, 50], [5, 255, 255]),
        'orange': ([10, 100, 100], [18, 255, 255]),
        'pineapple': ([30, 150, 50], [35, 255, 255]),
        'rainbow': ([40, 50, 50], [80, 255, 255])
    }
   
    def __init__(self):
        super().__init__()
        self.title('Pet Simulator 99 Companion v5 by xXGeminiXx/BeeBrained')
        self.geometry('200x300')  # Window size can be adjusted as needed 600x400 or blank to autosize
        self.monitoring_active = False  
        self.setup_hotkeys()  
        self.image_found = {}  # To keep track of found images
        self.load_reference_images()  # Make sure this is called before starting threads
        self.debug_mode = False
        self.fruit_usage_active = tk.BooleanVar(value=False)
        self.reference_images = {}  # To keep track of reference images
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Initialize the user interface.
        self.init_ui()

        self.wm_attributes('-topmost', 1)  # This will make the window stay on top
        self.wm_attributes('-alpha', 0.9)  # Set initial transparency to 90%
        # Transparency slider
        self.transparency_scale = ttk.Scale(self, from_=0.1, to=1.0, value=0.9, command=self.change_transparency)
        self.transparency_scale.pack(pady=5)
        self.next_fruit_time = None

        # Apply ttkbootstrap style to this root window
        style = tb.Style(theme='cyborg')
       
    def capture_fruit_area(self):
        # Define the region of the screen where the fruits appear
        # This is an example and you may need to adjust the coordinates
        fruit_region = (0, 0, 1920, 1080)  # Adjust to your specific screen area for fruits

        # Path to save the screenshot
        screenshot_path = os.path.join('C:\\Apps\\Automation Stuff\\PS99Companion\\reference_images', 'current_fruit.png')

        # Take a screenshot of the defined region
        screenshot = pyautogui.screenshot(region=fruit_region)
        screenshot.save(screenshot_path)

        return screenshot_path

    def load_reference_images(self):
        base_path = 'C:\\Apps\\Automation Stuff\\PS99Companion\\reference_images'
        categories = {
            'fruits': ['Banana.png', 'PS99_Apple.png', 'PS99_Orange.png', 'PS99_Pineapple.png', 'Rainbow.png'],
            # Assume potions and toys handled elsewhere or not needed for current task
        }
        self.reference_images = {'fruits': {}, 'potions': {}, 'toys': {}}

        for category, items in categories.items():
            for item in items:
                image_path = os.path.join(base_path, category, item)
                if os.path.exists(image_path):
                    self.reference_images[category][item[:-4]] = image_path  # Store without .png
                else:
                    print(f"Warning: Image file '{item}' not found for {category}")

    def start_monitoring(self):
        if not self.monitoring_active:
            self.monitoring_active = True
            print("Monitoring started.") if self.debug_mode else None
            threading.Thread(target=self.monitor_fruits, daemon=True).start()
            
    def on_close(self):
        # Custom shutdown sequence
        self.stop_all()
        self.destroy()  # This ensures the main window will close
        os._exit(0)  # This ensures any lingering threads are killed

    def stop_all(self):
        # Stop all running features and update the status label
        self.monitoring_active = False  # This will signal all threads to stop
        self.update_status('Shutting down...', style='warning')
        # Close any subprocess or threads if they are running
        if hasattr(self, 'fishing_process') and self.fishing_process.poll() is None:
            self.fishing_process.terminate()
        if hasattr(self, 'lucky_blocks_process') and self.lucky_blocks_process.poll() is None:
            self.lucky_blocks_process.terminate()
        # Give a small delay to allow threads to terminate
        time.sleep(0.5)
        self.update_status('All features stopped', style='danger')
        
    def toggle_fruit_usage(self):
        if self.fruit_usage_active.get():
            self.monitoring_active = True
            threading.Thread(target=self.monitor_fruits, daemon=True).start()
        else:
            self.monitoring_active = False

    def monitor_fruits(self):
        while self.monitoring_active and self.fruit_usage_active.get():
            now = datetime.now()
            if self.next_fruit_time is None or now >= self.next_fruit_time:
                self.update_status("Opening inventory for fruit usage...", style="info")
                self.open_inventory()
                found_fruit = self.scan_and_use_fruit()
                if not found_fruit:
                    self.update_status("Fruit not found. Will retry...", style="warning")
                else:
                    self.next_fruit_time = now + timedelta(minutes=5)
                    self.update_status(f"Fruit used. Next usage scheduled for {self.next_fruit_time.strftime('%H:%M:%S')}.", style="info")
            time.sleep(5)  # Short sleep to keep the loop responsive


    def scan_and_use_fruit(self):
        confidence = 0.5
        while confidence >= 0.5:  # Adjust as necessary
            for fruit_name, image_path in self.reference_images['fruits'].items():
                if self.debug_mode:
                    self.update_status(f"Scanning for {fruit_name} at confidence: {confidence:.2f}", style="info")
                location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
                if location:
                    pyautogui.click(location)
                    if self.debug_mode:
                        self.update_status(f"Used {fruit_name} at {location}.", style="success")
                    return True
            confidence -= 0.5
            if self.debug_mode:
                self.update_status(f"No fruit found. Reducing confidence to {confidence:.2f}", style="info")
        return False


    def open_inventory(self):
        # Simulate the key press to open inventory
        print("Opening inventory.") if self.debug_mode else None
        keyboard.press_and_release('f')  # Assuming 'i' opens the inventory
        time.sleep(2)  # Wait for inventory to open

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        print(f"Debug mode {'on' if self.debug_mode else 'off'}")

    def stop_monitoring(self):
        self.monitoring_active = False

    def convert_webp_to_png(self, image_path):
        """Converts a WEBP image to PNG format."""
        try:
            if image_path.lower().endswith('.webp'):
                img = Image.open(image_path)
                png_path = image_path.rsplit('.', 1)[0] + '.png'
                img.save(png_path, 'PNG')
                print(f"Converted {image_path} to PNG: {png_path}")
                return png_path
            else:
                return image_path
        except Exception as e:
            print(f"Error converting {image_path} to PNG: {e}")
            return image_path  # Return the original path if conversion fails

    def find_and_load_image(self, image_name, root_path='C:\\Apps\\Automation Stuff\\PS99Companion\\reference_images'):
        print(f"Searching for: {image_name}")
        search_pattern = re.compile(rf'(PS99_)?{re.escape(image_name.replace(" ", "_"))}.*\.(png|webp)$', re.IGNORECASE)

        for subdir, dirs, files in os.walk(root_path):
            for file in files:
                if search_pattern.match(file):
                    image_path = os.path.join(subdir, file)
                    print(f"Found and will use: {image_path}")
                    loaded_images[image_name] = image_path
                    if file.endswith('.webp'):
                        image_path = self.convert_webp_to_png(image_path)  # Correctly call within class
                    return image_path

        print(f"Image '{image_name}' not found in {root_path}")
        return None
        
    def find_fruits_by_color(self, image_path):
        image = cv2.imread(image_path)
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Defining the ROI, bottom left 8th of the image
        height, width, _ = image.shape
        roi = (0, int(height*0.875), width//8, height)

        # Cropping the image to the ROI
        hsv_roi = hsv_image[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]

        for fruit, (hsv_lower, hsv_upper) in self.fruit_color_ranges.items():
            # Special multi-color detection logic for rainbow fruit
            if fruit == 'rainbow':
                # Implement multi-color detection logic for rainbow fruit here
                pass
            else:
                lower_bound = np.array(hsv_lower)
                upper_bound = np.array(hsv_upper)

                # Create a mask for the color range and find contours in the ROI
                mask = cv2.inRange(hsv_roi, lower_bound, upper_bound)
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    # Filter out contours that do not meet expected criteria
                    if 100 < area < 10000:  # Adjust area thresholds as needed
                        x, y, w, h = cv2.boundingRect(cnt)
                        if 0.75 < w/h < 1.25:  # Adjust aspect ratio thresholds for fruit shapes
                            x += roi[0]  # Adjust x to account for ROI
                            y += roi[1]  # Adjust y to account for ROI
                            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            if self.debug_mode:
                                cv2.putText(image, fruit, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                                cv2.imshow(f"{fruit} detected", image)
                                cv2.waitKey(0)

        # In debug mode, show the full image with all detections
        if self.debug_mode:
            cv2.imshow("All Detections", image)
            cv2.waitKey(0)
                
    def recognize_items(self, category):
        recognized_items = {}
        if hasattr(self, 'reference_images') and category in self.reference_images:
            for item, image_path in self.reference_images[category].items():
                if image_path:
                    confidence_level = 0.9
                    while confidence_level > 0.3:  # Adjust the lower limit as needed.
                        location = pyautogui.locateOnScreen(image_path, confidence=confidence_level)
                        if location:
                            if self.debug_mode:
                                print(f"Detected {item} with confidence {confidence_level}")
                                self.show_detected_area(location)
                            recognized_items[item] = location
                            break  # If found, break out of the loop.
                        confidence_level -= 0.05  # Decrease confidence level.
        return recognized_items

    def show_detected_area(self, location):
    # Draw a rectangle around the detected area
        top_left_x, top_left_y, width, height = location
        img = pyautogui.screenshot(region=(top_left_x, top_left_y, width, height))
        img.show()
    
    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        print(f"Debug mode {'on' if self.debug_mode else 'off'}")

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
        
    def change_transparency(self, value):
        self.wm_attributes('-alpha', float(value))

    def setup_hotkeys(self):
        # Bind keyboard hotkeys to feature toggles
        # These hotkeys will be global (system-wide)
        keyboard.add_hotkey('ctrl+f1', self.toggle_fishing, suppress=True)
        keyboard.add_hotkey('ctrl+f2', self.toggle_item_recognition, suppress=True)
        keyboard.add_hotkey('ctrl+f3', self.toggle_buff_monitoring, suppress=True)
        keyboard.add_hotkey('ctrl+f4', self.toggle_lucky_blocks, suppress=True)
        keyboard.add_hotkey('ctrl+d', self.toggle_debug_mode, suppress=True)

        # Update the GUI to show the hotkeys or print them to the console
        print("Global Hotkeys Activated")

    def buff_monitoring_loop(self):
        # Call self.after to check for buffs every second (1000 milliseconds)
        if self.monitoring_active:
            self.check_for_buffs()
            self.after(1000, self.buff_monitoring_loop)
            self.find_fruits_by_color(screenshot_path, fruit_color_ranges)

            
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
        ttk.Checkbutton(feature_frame, text='Fruit Usage', variable=self.fruit_usage_active, 
                        onvalue=True, offvalue=False, command=self.toggle_fruit_usage).pack(anchor='w')
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

        # Take a screenshot of the fruit area and analyze colors
        screenshot_path = self.capture_fruit_area()
        self.find_fruits_by_color(screenshot_path)
        
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
        keyboard.add_hotkey('ctrl+d', self.toggle_debug_mode, suppress=True)

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
    main()
