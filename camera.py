import cv2 as cv
import os
import numpy as np
import time

class Camera:
    def __init__(self):
        # Based on diagnostic results: Camera 0 works perfectly
        self.camera_index = 0
        self.camera_backend = cv.CAP_V4L2  # V4L2 backend confirmed working
        self.cap = None
        
        # Try multiple backends if needed
        self.backends_to_try = [
            (cv.CAP_V4L2, "V4L2"),
            (cv.CAP_ANY, "CAP_ANY"),
            (cv.CAP_GSTREAMER, "GStreamer"),
        ]
        
        self.init_camera()

    def init_camera(self):
        print("🎥 INITIALIZING UBUNTU SERVER CAMERA")
        
        for backend, backend_name in self.backends_to_try:
            try:
                print(f"🔍 Trying {backend_name} backend for camera at index {self.camera_index}...")
                self.cap = cv.VideoCapture(self.camera_index, backend)
                
                if not self.cap.isOpened():
                    print(f"❌ Failed to open camera with {backend_name}")
                    continue
                
                # Give camera extra time to initialize before first read
                print("⏳ Waiting for camera to stabilize...")
                time.sleep(2.0)
                
                # Set basic properties first to help with stability
                self.cap.set(cv.CAP_PROP_BUFFERSIZE, 1)
                self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
                time.sleep(0.5)
                
                # Try multiple frame reads with increasing timeouts
                test_frame = None
                ret = False
                for attempt in range(5):
                    print(f"📹 Frame capture attempt {attempt + 1}/5...")
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        print(f"✅ Successfully captured frame on attempt {attempt + 1}")
                        break
                    else:
                        print(f"⚠️  Attempt {attempt + 1} failed, retrying...")
                        time.sleep(1.0)
                        # Clear buffer
                        for _ in range(3):
                            self.cap.read()
                
                if ret and test_frame is not None:
                    self.camera_backend = backend
                    print(f"✅ Successfully opened camera at index {self.camera_index}")
                    print(f"   📱 Device: /dev/video{self.camera_index}")
                    print(f"   🔧 Backend: {backend_name}")
                    print(f"   📊 Test frame: {test_frame.shape[1]}x{test_frame.shape[0]}")
                    
                    # Configure camera properties (conservative settings)
                    self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480) 
                    self.cap.set(cv.CAP_PROP_FPS, 15)
                    self.cap.set(cv.CAP_PROP_BUFFERSIZE, 1)
                    
                    # Try to set MJPEG format for better performance
                    try:
                        self.cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                    except:
                        print("⚠️  MJPEG format not supported, using default")
                    
                    # Verify settings
                    actual_width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
                    actual_height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
                    actual_fps = self.cap.get(cv.CAP_PROP_FPS)
                    
                    print(f"📊 Camera Configuration:")
                    print(f"   Resolution: {actual_width}x{actual_height}")
                    print(f"   FPS: {actual_fps:.1f}")
                    print(f"   Buffer Size: 1")
                    
                    # Give camera time to stabilize
                    time.sleep(1.0)
                    
                    # Final stability test
                    test_success_count = 0
                    for i in range(3):
                        ret, _ = self.cap.read()
                        if ret:
                            test_success_count += 1
                        time.sleep(0.1)
                    
                    if test_success_count >= 2:
                        print(f"✅ Camera initialization successful! ({test_success_count}/3 test frames)")
                        return  # Success!
                    else:
                        print(f"⚠️  Camera unstable with {backend_name}: only {test_success_count}/3 test frames captured")
                        self.cap.release()
                        continue
                else:
                    print(f"❌ {backend_name} backend opened camera but cannot capture frames")
                    self.cap.release()
                    continue
                    
            except Exception as e:
                print(f"❌ {backend_name} backend failed: {e}")
                if self.cap:
                    self.cap.release()
                continue
        
        # If we get here, all backends failed
        print(f"❌ Camera initialization failed with all backends")
        print("🔧 Troubleshooting suggestions:")
        print("   1. Check camera connection: lsusb | grep -i camera")
        print("   2. Check video devices: ls -la /dev/video*")
        print("   3. Test manually: python3 ubuntu_camera_debug.py")
        print("   4. Kill any processes using camera: sudo fuser -k /dev/video0")
        print("   5. Try different USB port")
        print("   6. Check camera permissions: sudo usermod -a -G video $USER")
        raise Exception(f"Camera initialization failed with all available backends")

    def openCamera(self):
        """Reopen camera if it was closed"""
        if self.cap is None or not self.cap.isOpened():
            print(f"🔄 Reopening camera at index {self.camera_index}")
            self.cap = cv.VideoCapture(self.camera_index, self.camera_backend)
            if not self.cap.isOpened():
                print("⚠️  Failed to reopen camera, trying full reinit...")
                self.init_camera()

    def get_frame(self):
        """Get a frame from the camera"""
        if self.cap is None or not self.cap.isOpened():
            print("⚠️  Camera not opened, attempting to open...")
            try:
                self.openCamera()
            except Exception as e:
                print(f"❌ Error reopening camera: {e}")
                # Return a black frame as fallback
                return np.zeros((480, 640, 3), dtype=np.uint8)
            
        ret, frame = self.cap.read()
        if not ret or frame is None:
            print("⚠️  Failed to read frame. Attempting to reinitialize camera...")
            try:
                self.init_camera()
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    print("❌ Still cannot read frames after reinit")
                    return np.zeros((480, 640, 3), dtype=np.uint8)
            except Exception as e:
                print(f"❌ Failed to reinitialize camera: {e}")
                return np.zeros((480, 640, 3), dtype=np.uint8)

        return frame

    def is_opened(self):
        """Check if the camera is opened and working"""
        if self.cap is None:
            return False
        
        if not self.cap.isOpened():
            return False
            
        # Quick test to see if we can actually read a frame
        try:
            ret, _ = self.cap.read()
            return ret
        except:
            return False

    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print(" Camera resources released")
        cv.destroyAllWindows()
        
    def stop(self):
        """Alias for release"""
        self.release()