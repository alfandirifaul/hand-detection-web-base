import cv2 as cv
import numpy as np
import time

class Camera:
    def __init__(self):
        self.camera_index = 0
        self.cap = None
        self.init_camera()

    def init_camera(self):
        """Initialize camera with proper error handling"""
        print("🎥 Opening camera...")
        
        self.cap = cv.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("❌ Failed to open camera")
            return False

        print("✅ Camera opened successfully")
        return True

    def get_frame(self):
        ret, frame = self.cap.read()
        cv.imshow("Camera Feed", frame)
        if not ret or frame is None:
            print("⚠️  Failed to read frame")
            return None

        return frame

    def is_opened(self):
        """Check if the camera is opened"""
        return self.cap is not None and self.cap.isOpened()

    def openCamera(self):
        """Reopen camera if it was closed"""
        if self.cap is None or not self.cap.isOpened():
            print("🔄 Reopening camera...")
            success = self.init_camera()
            return success
        return True

    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("📷 Camera released")
        
    def stop(self):
        """Alias for release"""
        self.release()

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.release()
