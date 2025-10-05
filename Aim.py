import winsound
import win32api
import win32con
import numpy as np
import random
import time
import cv2
import mss


class AimConfig:
    """Configuration settings for the aim assist program"""
    
    def __init__(self):
        self.screen_width = 1920
        self.screen_height = 1080
        self.capture_size = 240
        
        # Calculate center coordinates
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        self.capture_radius = self.capture_size // 2
        
        # Define capture region around crosshair
        self.capture_region = {
            "top": self.center_y - self.capture_radius,
            "left": self.center_x - self.capture_radius,
            "width": self.capture_size,
            "height": self.capture_size
        }


class AimAssist:
    """Main aim assist controller"""
    
    def __init__(self):
        self.config = AimConfig()
        self.screen_capture = mss.mss()
        
        # Load and prepare template
        self.template = self._load_template("enemyIndic3.png")
        self.template_w, self.template_h = self.template.shape[::-1]
        self.template_center_x = self.template_w // 2
        self.template_center_y = self.template_h // 2
        
        # Sensitivity settings
        self.roblox_sensitivity = 0.55
        self.pf_mouse_sensitivity = 0.5
        self.pf_aim_sensitivity = 1
        self.movement_compensation = 0.2
        
        self.final_sensitivity = self._calculate_sensitivity()
    
    def _load_template(self, filename):
        """Load and convert template image to grayscale"""
        template = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        return cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    def _calculate_sensitivity(self):
        """Calculate final sensitivity multiplier"""
        pf_sensitivity = self.pf_mouse_sensitivity * self.pf_aim_sensitivity
        return ((self.roblox_sensitivity * pf_sensitivity) / 0.55) + self.movement_compensation
    
    def should_exit(self):
        """Check if exit key is pressed (Numpad 6)"""
        return win32api.GetAsyncKeyState(0x6) < 0
    
    def is_aiming(self):
        """Check if right mouse button is pressed"""
        return win32api.GetAsyncKeyState(0x02) < 0
    
    def capture_game_frame(self):
        """Capture screen region around crosshair"""
        frame = np.array(self.screen_capture.grab(self.config.capture_region))
        return cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
    
    def find_target(self, game_frame):
        """Find target using template matching"""
        result = cv2.matchTemplate(game_frame, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Confidence threshold (adjust if needed)
        if max_val >= 0.8:
            return max_loc, max_val
        return None, max_val
    
    def calculate_aim_offset(self, target_location):
        """Calculate mouse movement needed to aim at target"""
        target_x = target_location[0] + self.template_center_x
        target_y = target_location[1] + self.template_center_y
        
        # Calculate offset from crosshair center
        offset_x = (-(self.config.capture_radius - target_x)) * self.final_sensitivity
        offset_y = (-(self.config.capture_radius - target_y)) * self.final_sensitivity
        
        return int(offset_x), int(offset_y)
    
    def perform_aim_action(self, offset_x, offset_y):
        """Move mouse and perform click action"""
        # Move mouse to target
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, offset_x, offset_y, 0, 0)
        
        # Simulate mouse click
        win32api.mouse_event(0x0002, 0, 0, 0, 0)  # Mouse down
        time.sleep(random.uniform(0.01, 0.03))
        win32api.mouse_event(0x0004, 0, 0, 0, 0)  # Mouse up
    
    def run(self):
        """Main program loop"""
        print("Aim assist started. Press Numpad 6 to exit.")
        
        while True:
            time.sleep(0.001)  # Small delay to reduce CPU usage
            
            if self.should_exit():
                winsound.Beep(1000, 10)
                break
            
            if self.is_aiming():
                game_frame = self.capture_game_frame()
                target_location, confidence = self.find_target(game_frame)
                
                if target_location:
                    offset_x, offset_y = self.calculate_aim_offset(target_location)
                    self.perform_aim_action(offset_x, offset_y)
        
        print("Aim assist stopped.")


if __name__ == "__main__":
    aim_assist = AimAssist()
    aim_assist.run()
