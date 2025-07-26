import cv2 as cv
import os
import numpy as np
import time

class Camera:
    def __init__(self):
        # Try different camera indices on Ubuntu servers
        # 0 is usually the first camera, but we'll try others if that fails
        self.camera_index = 0
        self.cap = None
        self.init_camera()

    def init_camera(self):
        # Try camera indices 0 through 2 to find a working camera
        available_cameras = self._find_available_cameras(3)
        
        if not available_cameras:
            print("No cameras detected on the system")
            raise Exception("Could not find any video devices")
        
        print(f"Available cameras: {available_cameras}")
        self.camera_index = available_cameras[0]
        
        try:
            self.cap = cv.VideoCapture(self.camera_index)
            if self.cap.isOpened():
                print(f"Successfully opened camera at index {self.camera_index}")
                
                # Set camera properties for better streaming performance
                self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv.CAP_PROP_FPS, 15)
                
                # Give camera time to initialize
                time.sleep(0.5)
            else:
                raise Exception(f"Failed to open camera at index {self.camera_index}")
        except Exception as e:
            print(f"Error initializing camera: {e}")
            raise

    def _find_available_cameras(self, max_to_check=3):
        """Find available cameras on the system"""
        available = []
        
        for i in range(max_to_check):
            try:
                print(f"Checking camera index {i}...")
                temp_camera = cv.VideoCapture(i)
                if temp_camera.isOpened():
                    available.append(i)
                    print(f"Camera {i} is available")
                temp_camera.release()
            except Exception as e:
                print(f"Error checking camera {i}: {e}")
        
        return available

    def openCamera(self):
        if self.cap is None or not self.cap.isOpened():
            print(f"Reopening camera at index {self.camera_index}")
            self.cap = cv.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                self.init_camera()  # Try to find another camera if the previous one failed
                if self.cap is None or not self.cap.isOpened():
                    raise Exception("Could not open video device")

    def get_frame(self):
        if self.cap is None or not self.cap.isOpened():
            try:
                self.openCamera()
            except Exception as e:
                print(f"Error reopening camera: {e}")
                # Return a black frame as fallback
                return np.zeros((480, 640, 3), dtype=np.uint8)
            
        ret, frame = self.cap.read()
        # Do not flip the frame as we'll control this in the UI
        if not ret:
            print("Warning: Failed to read frame. Attempting to reinitialize camera...")
            try:
                self.init_camera()
                _, frame = self.cap.read()
                if not _:
                    return np.zeros((480, 640, 3), dtype=np.uint8)  # Return black frame as fallback
            except Exception as e:
                print(f"Failed to reinitialize camera: {e}")
                return np.zeros((480, 640, 3), dtype=np.uint8)  # Return black frame as fallback

        return frame

    def is_opened(self):
        """Check if the camera is opened"""
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("Camera resources released")
        cv.destroyAllWindows()
        
    def stop(self):
        """Alias for release"""
        self.release()