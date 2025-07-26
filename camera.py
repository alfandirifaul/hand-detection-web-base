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
        self.init_camera()

    def init_camera(self):
        print("🎥 INITIALIZING UBUNTU SERVER CAMERA")
        
        try:
            print(f"🔍 Opening camera at index {self.camera_index} with V4L2 backend...")
            self.cap = cv.VideoCapture(self.camera_index, self.camera_backend)
            
            if not self.cap.isOpened():
                print("❌ Failed to open camera with V4L2, trying with CAP_ANY...")
                self.cap = cv.VideoCapture(self.camera_index, cv.CAP_ANY)
            
            if self.cap.isOpened():
                # Test frame capture immediately
                ret, test_frame = self.cap.read()
                if ret and test_frame is not None:
                    print(f"✅ Successfully opened camera at index {self.camera_index}")
                    print(f"   📱 Device: /dev/video{self.camera_index}")
                    print(f"   🔧 Backend: {self.cap.getBackendName()}")
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
                        print(f"⚠️  Camera unstable: only {test_success_count}/3 test frames captured")
                        raise Exception("Camera opened but frame capture is unstable")
                else:
                    print("❌ Camera opened but cannot capture frames")
                    raise Exception("Camera opened but cannot read frames")
            else:
                print("❌ Failed to open camera")
                raise Exception("Could not open camera")
                
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            print("🔧 Troubleshooting suggestions:")
            print("   1. Check camera connection: lsusb | grep -i camera")
            print("   2. Check video devices: ls -la /dev/video*")
            print("   3. Test manually: python3 ubuntu_camera_debug.py")
            print("   4. Restart camera service: sudo systemctl restart camera-service")
            raise Exception(f"Camera initialization failed: {e}")

    def openCamera(self):
        """Reopen camera if it was closed"""
        if self.cap is None or not self.cap.isOpened():
            print(f"🔄 Reopening camera at index {self.camera_index}")
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
            print("📱 Camera resources released")
        cv.destroyAllWindows()
        
    def stop(self):
        """Alias for release"""
        self.release()

    def _find_available_cameras(self, max_to_check=10):
        """Find available cameras on the system with detailed Ubuntu server debugging"""
        available = []
        
        print("=" * 60)
        print("🎥 SCANNING FOR CAMERAS ON UBUNTU SERVER")
        print("=" * 60)
        
        # Check if running as root or with proper permissions
        try:
            import os
            user_groups = os.popen('groups').read().strip()
            if 'video' not in user_groups:
                print("⚠️  WARNING: User is not in 'video' group!")
                print("   Fix: sudo usermod -a -G video $USER")
                print("   Then logout and login again")
            else:
                print("✅ User is in 'video' group")
        except:
            print("⚠️  Could not check user groups")
        
        # Check /dev/video* devices first
        try:
            video_devices = [d for d in os.listdir('/dev') if d.startswith('video')]
            video_devices.sort()
            if video_devices:
                print(f"📱 Video devices found: {', '.join(video_devices)}")
                for device in video_devices:
                    device_path = f"/dev/{device}"
                    try:
                        stat_info = os.stat(device_path)
                        permissions = oct(stat_info.st_mode)[-3:]
                        print(f"   {device_path}: permissions {permissions}")
                    except Exception as e:
                        print(f"   {device_path}: error {e}")
            else:
                print("❌ No /dev/video* devices found!")
                print("   Install: sudo apt install v4l-utils")
                print("   Check: lsusb | grep -i camera")
        except Exception as e:
            print(f"❌ Error checking /dev/: {e}")
        
        # Test OpenCV camera indices
        for i in range(max_to_check):
            print(f"\n🔍 Testing camera index {i}...")
            
            try:
                # Try different OpenCV backends for Ubuntu compatibility
                backends_to_try = [
                    cv.CAP_V4L2,    # Video4Linux2 (most common on Ubuntu)
                    cv.CAP_ANY,     # Auto-detect
                    cv.CAP_GSTREAMER # GStreamer (good for Ubuntu)
                ]
                
                camera_opened = False
                best_backend = None
                
                for backend in backends_to_try:
                    try:
                        temp_camera = cv.VideoCapture(i, backend)
                        if temp_camera.isOpened():
                            # Test if we can actually read a frame
                            ret, frame = temp_camera.read()
                            if ret and frame is not None:
                                backend_name = temp_camera.getBackendName()
                                print(f"✅ Camera {i} works with backend: {backend_name}")
                                
                                # Get camera properties
                                width = int(temp_camera.get(cv.CAP_PROP_FRAME_WIDTH))
                                height = int(temp_camera.get(cv.CAP_PROP_FRAME_HEIGHT))
                                fps = temp_camera.get(cv.CAP_PROP_FPS)
                                
                                camera_info = {
                                    'index': i,
                                    'backend': backend,
                                    'backend_name': backend_name,
                                    'width': width,
                                    'height': height,
                                    'fps': fps,
                                    'device_path': f"/dev/video{i}"
                                }
                                
                                available.append(camera_info)
                                camera_opened = True
                                best_backend = backend_name
                                
                                print(f"   📊 Resolution: {width}x{height}")
                                print(f"   📊 FPS: {fps:.1f}")
                                print(f"   📱 Device: /dev/video{i}")
                                
                                temp_camera.release()
                                break
                            else:
                                print(f"❌ Camera {i}: Backend {temp_camera.getBackendName()} - Cannot read frames")
                        temp_camera.release()
                    except Exception as e:
                        print(f"❌ Camera {i}: Backend error - {e}")
                
                if not camera_opened:
                    print(f"❌ Camera {i}: No working backends found")
                    
            except Exception as e:
                print(f"❌ Camera {i}: General error - {e}")
        
        print("\n" + "=" * 60)
        if available:
            print(f"✅ FOUND {len(available)} WORKING CAMERA(S)")
            for cam in available:
                print(f"   🎥 Index {cam['index']}: {cam['width']}x{cam['height']} @ {cam['fps']:.1f}fps")
                print(f"      Backend: {cam['backend_name']} | Device: {cam['device_path']}")
        else:
            print("❌ NO WORKING CAMERAS FOUND!")
            print("\n🔧 Ubuntu Camera Troubleshooting:")
            print("   1. Install: sudo apt update && sudo apt install v4l-utils")
            print("   2. Check devices: v4l2-ctl --list-devices")
            print("   3. Add to group: sudo usermod -a -G video $USER")
            print("   4. Check USB: lsusb | grep -i camera")
            print("   5. Permissions: ls -la /dev/video*")
            print("   6. Test manually: python3 ubuntu_camera_debug.py")
        print("=" * 60)
        
        return available

    def openCamera(self):
        if self.cap is None or not self.cap.isOpened():
            print(f"🔄 Reopening Ubuntu server camera at index {self.camera_index} (/dev/video{self.camera_index})")
            
            # Use the same backend that worked during initialization
            if hasattr(self, 'camera_backend'):
                self.cap = cv.VideoCapture(self.camera_index, self.camera_backend)
            else:
                self.cap = cv.VideoCapture(self.camera_index)
                
            if not self.cap.isOpened():
                print("⚠️  Failed to reopen camera, scanning for alternatives...")
                self.init_camera()  # Try to find another camera if the previous one failed
                if self.cap is None or not self.cap.isOpened():
                    raise Exception("Could not open video device on Ubuntu server")

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