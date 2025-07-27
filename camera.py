import cv2 as cv
import numpy as np
import time

class Camera:
    def __init__(self):
        self.camera_index = 0
        self.cap = None
        self.init_camera()

    def init_camera(self):
        """Initialize camera with proper error handling and RPi optimizations"""
        print("🎥 Opening camera...")
        
        self.cap = cv.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("❌ Failed to open camera")
            return False

        # Optimize for Raspberry Pi performance
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv.CAP_PROP_FPS, 10)  # Lower FPS for stable performance
        self.cap.set(cv.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to minimize delay
        
        # Try to use hardware acceleration
        self.cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        print("✅ Camera opened successfully")
        return True

    def get_frame(self):
        # Clear buffer to get latest frame (reduces delay)
        for _ in range(2):
            ret, frame = self.cap.read()
            if not ret:
                break
                
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
