import cv2 as cv
import numpy as np
import time
import threading

class Camera:
    def __init__(self):
        self.camera_index = 0
        self.cap = None
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        self.capturing = False
        self.init_camera()

    def init_camera(self):
        """Initialize camera with proper error handling and RPi optimizations"""
        print("🎥 Opening camera...")
        
        self.cap = cv.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print("❌ Failed to open camera")
            return False

        # Optimize for real-time performance
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv.CAP_PROP_FPS, 30)  # Higher FPS for smoother capture
        self.cap.set(cv.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer
        
        # Additional optimizations
        self.cap.set(cv.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Faster exposure
        self.cap.set(cv.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus for speed
        
        # Try to use hardware acceleration
        self.cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        # Start continuous capture thread
        self.start_capture_thread()

        print("✅ Camera opened successfully")
        return True

    def start_capture_thread(self):
        """Start a separate thread for continuous frame capture"""
        self.capturing = True
        self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()

    def _capture_frames(self):
        """Continuously capture frames in a separate thread"""
        while self.capturing and self.cap is not None:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                with self.frame_lock:
                    self.latest_frame = frame.copy()
            # No sleep - capture as fast as possible

    def get_frame(self):
        """Get the latest frame (non-blocking)"""
        with self.frame_lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
        return None

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
        self.capturing = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        
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
