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
        
        # Try multiple approaches to open the camera
        backends_to_try = [
            (cv.CAP_GSTREAMER, "GStreamer"),
            (cv.CAP_FFMPEG, "FFmpeg"), 
            (cv.CAP_ANY, "CAP_ANY"),
            (cv.CAP_V4L2, "V4L2"),
        ]
        
        for backend, name in backends_to_try:
            try:
                print(f"🔍 Trying {name} backend...")
                self.cap = cv.VideoCapture(self.camera_index, backend)
                
                if not self.cap.isOpened():
                    print(f"❌ {name} backend failed to open camera")
                    continue
                
                # Set some basic properties that might help
                self.cap.set(cv.CAP_PROP_BUFFERSIZE, 1)
                self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
                
                # Give camera time to initialize
                print(f"⏳ Waiting for {name} to stabilize...")
                time.sleep(2.0)
                
                # Test frame reading with multiple attempts
                for attempt in range(3):
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        print(f"✅ Camera opened successfully with {name} backend")
                        print(f"   📊 Frame size: {frame.shape[1]}x{frame.shape[0]}")
                        return  # Success!
                    else:
                        print(f"⚠️  Frame read attempt {attempt + 1} failed, retrying...")
                        time.sleep(1.0)
                
                # If we get here, this backend didn't work
                print(f"❌ {name} backend opened camera but couldn't read frames")
                self.cap.release()
                
            except Exception as e:
                print(f"❌ {name} backend error: {e}")
                if self.cap:
                    self.cap.release()
                continue
        
        # If all backends failed
        self.cap = None
        raise Exception("All camera backends failed")

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
