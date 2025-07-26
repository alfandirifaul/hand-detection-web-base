import cv2 as cv
import os
import numpy as np
import time

class Camera:
    def __init__(self):
        # Try different camera indices on Ubuntu servers
        # 0 is usually the first camera, but we'll try others if that fails
        self.camera_index = 0
        self.camera_backend = cv.CAP_ANY  # Default backend
        self.cap = None
        self.init_camera()

    def init_camera(self):
        # Scan for available cameras with detailed Ubuntu server analysis
        available_cameras = self._find_available_cameras(10)
        
        if not available_cameras:
            print("❌ No cameras detected on the Ubuntu server")
            print("\n🔧 Quick fixes to try:")
            print("   sudo apt update && sudo apt install v4l-utils")
            print("   sudo usermod -a -G video $USER")
            print("   v4l2-ctl --list-devices")
            print("   python3 ubuntu_camera_debug.py")
            raise Exception("Could not find any video devices on Ubuntu server")
        
        # Select the best camera (first working one)
        best_camera = available_cameras[0]
        self.camera_index = best_camera['index']
        self.camera_backend = best_camera['backend']
        
        print(f"\n🎥 INITIALIZING UBUNTU SERVER CAMERA")
        print(f"   📱 Port: /dev/video{self.camera_index}")
        print(f"   🔧 Backend: {best_camera['backend_name']}")
        print(f"   📊 Default: {best_camera['width']}x{best_camera['height']} @ {best_camera['fps']:.1f}fps")
        
        try:
            # Use the specific backend that worked during detection
            self.cap = cv.VideoCapture(self.camera_index, self.camera_backend)
            
            if self.cap.isOpened():
                print(f"✅ Successfully opened camera at index {self.camera_index}")
                
                # Set optimal properties for Ubuntu server streaming
                # Use 720p if supported, otherwise fall back to VGA
                target_width = 1280 if best_camera['width'] >= 1280 else 640
                target_height = 720 if best_camera['height'] >= 720 else 480
                
                print(f"🎯 Setting resolution to {target_width}x{target_height}")
                
                # Configure camera properties with Ubuntu-specific optimizations
                self.cap.set(cv.CAP_PROP_FRAME_WIDTH, target_width)
                self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, target_height)
                self.cap.set(cv.CAP_PROP_FPS, 15)  # Conservative FPS for stability
                
                # Ubuntu server optimizations
                self.cap.set(cv.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency
                self.cap.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'))  # MJPEG for performance
                
                # Additional Ubuntu-specific settings
                try:
                    self.cap.set(cv.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Disable auto-exposure for consistency
                    self.cap.set(cv.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus for stability
                except:
                    pass  # Some cameras don't support these properties
                
                # Give camera time to initialize
                time.sleep(1.5)  # Longer delay for Ubuntu server
                
                # Verify the actual settings
                actual_width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
                actual_fps = self.cap.get(cv.CAP_PROP_FPS)
                buffer_size = int(self.cap.get(cv.CAP_PROP_BUFFERSIZE))
                
                print(f"📊 Camera Configuration Applied:")
                print(f"   Resolution: {actual_width}x{actual_height}")
                print(f"   FPS: {actual_fps:.1f}")
                print(f"   Buffer Size: {buffer_size}")
                print(f"   FOURCC: MJPG")
                
                # Test frame capture with retries
                test_success = False
                for attempt in range(3):
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        print(f"✅ Test frame captured successfully: {test_frame.shape}")
                        test_success = True
                        break
                    else:
                        print(f"⚠️  Test frame attempt {attempt + 1}/3 failed")
                        time.sleep(0.5)
                
                if not test_success:
                    print("❌ Warning: Cannot capture test frames reliably")
                    raise Exception("Camera opened but cannot capture frames")
                
            else:
                raise Exception(f"Failed to open camera at index {self.camera_index} with backend {best_camera['backend_name']}")
                
        except Exception as e:
            print(f"❌ Error initializing Ubuntu server camera: {e}")
            print("\n🔧 Try running the debug script: python3 ubuntu_camera_debug.py")
            raise

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