import cv2 as cv
import os
import numpy as np
import time

class Camera:
    def __init__(self):
        self.camera_index = 0
        self.cap = None
        self.init_camera()

    def init_camera(self):
        print("🎥 Opening camera...")
        
        try:
            # Try with CAP_ANY backend to avoid V4L2 timeout issues
            self.cap = cv.VideoCapture(self.camera_index, cv.CAP_ANY)
            
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
            
            # Give camera a moment to initialize
            time.sleep(1.0)
            
            # Test if we can read frames
            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise Exception("Could not read frame from camera")
            
            print(f"✅ Camera opened successfully at index {self.camera_index}")
            print(f"   � Frame size: {frame.shape[1]}x{frame.shape[0]}")
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            if self.cap:
                self.cap.release()
                self.cap = None
            raise

    def openCamera(self):
        """Reopen camera if it was closed"""
        if self.cap is None or not self.cap.isOpened():
            print(f"🔄 Reopening camera...")
            self.init_camera()

    def get_frame(self):
        """Get a frame from the camera"""
        if self.cap is None or not self.cap.isOpened():
            print("⚠️  Camera not opened")
            return np.zeros((480, 640, 3), dtype=np.uint8)
            
        ret, frame = self.cap.read()
        if not ret or frame is None:
            print("⚠️  Failed to read frame")
            return np.zeros((480, 640, 3), dtype=np.uint8)

        return frame

    def is_opened(self):
        """Check if the camera is opened"""
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("📷 Camera released")
        
    def stop(self):
        """Alias for release"""
        self.release()