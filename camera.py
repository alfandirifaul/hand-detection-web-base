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
        
        # Try different backends in order of preference
        backends = [
            cv.CAP_V4L2,    # Linux default
            cv.CAP_GSTREAMER,  # Alternative for Linux
            cv.CAP_ANY      # Let OpenCV choose
        ]
        
        for backend in backends:
            try:
                print(f"   Trying backend: {backend}")
                self.cap = cv.VideoCapture(self.camera_index, backend)
                
                if not self.cap.isOpened():
                    print(f"   ❌ Failed to open with backend {backend}")
                    continue
                
                # Set buffer size to reduce latency
                self.cap.set(cv.CAP_PROP_BUFFERSIZE, 1)
                
                # Set reasonable resolution
                self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
                
                # Set FPS
                self.cap.set(cv.CAP_PROP_FPS, 30)
                
                # Give camera time to warm up
                time.sleep(1)
                
                # Test if we can read a frame
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    print(f"   ✅ Camera opened successfully with backend {backend}")
                    print(f"   📐 Resolution: {int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))}")
                    print(f"   🎬 FPS: {self.cap.get(cv.CAP_PROP_FPS)}")
                    return  # Success!
                else:
                    print(f"   ❌ Cannot read frames with backend {backend}")
                    self.cap.release()
                    self.cap = None
                    
            except Exception as e:
                print(f"   ❌ Exception with backend {backend}: {e}")
                if self.cap:
                    self.cap.release()
                    self.cap = None
        
        # If we get here, all backends failed
        raise Exception("Could not initialize camera with any backend")

    def get_frame(self):
        """Get a frame from the camera"""
        if self.cap is None or not self.cap.isOpened():
            print("⚠️  Camera not opened")
            return None
            
        ret, frame = self.cap.read()
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
            self.init_camera()

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
