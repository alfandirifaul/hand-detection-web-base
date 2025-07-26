#!/usr/bin/env python3
"""
Camera Test Script for Ubuntu Server
This script tests camera availability and prints detailed information about detected cameras.
"""

import cv2
import os
import sys
import subprocess
import platform
from datetime import datetime

class CameraTest:
    def __init__(self):
        self.available_cameras = []
        self.system_info = self.get_system_info()
        
    def get_system_info(self):
        """Get system information"""
        info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
        return info
    
    def print_header(self):
        """Print test header with system information"""
        print("=" * 80)
        print("🎥 CAMERA DETECTION TEST FOR UBUNTU SERVER")
        print("=" * 80)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Platform: {self.system_info['platform']}")
        print(f"System: {self.system_info['system']} {self.system_info['release']}")
        print(f"Architecture: {self.system_info['machine']}")
        print("=" * 80)
    
    def check_video_devices(self):
        """Check for video devices using system commands"""
        print("\n📹 CHECKING VIDEO DEVICES...")
        print("-" * 50)
        
        # Check /dev/video* devices
        video_devices = []
        try:
            devices = os.listdir('/dev')
            video_devices = [d for d in devices if d.startswith('video')]
            video_devices.sort()
            
            if video_devices:
                print(f"✅ Found {len(video_devices)} video device(s):")
                for device in video_devices:
                    print(f"   • /dev/{device}")
            else:
                print("❌ No video devices found in /dev/")
                
        except Exception as e:
            print(f"❌ Error checking /dev/ directory: {e}")
        
        # Try v4l2-ctl command if available
        try:
            result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                print("\n📋 V4L2 Device Information:")
                print(result.stdout)
            else:
                print("\n⚠️  v4l2-ctl not available or no output")
        except FileNotFoundError:
            print("\n⚠️  v4l2-ctl command not found (install v4l-utils for detailed info)")
        except subprocess.TimeoutExpired:
            print("\n⚠️  v4l2-ctl command timed out")
        except Exception as e:
            print(f"\n⚠️  Error running v4l2-ctl: {e}")
        
        return video_devices
    
    def test_opencv_cameras(self, max_cameras=10):
        """Test camera access using OpenCV"""
        print(f"\n🔍 TESTING OPENCV CAMERA ACCESS (indices 0-{max_cameras-1})...")
        print("-" * 60)
        
        working_cameras = []
        
        for i in range(max_cameras):
            print(f"Testing camera index {i}... ", end="", flush=True)
            
            try:
                # Create capture object
                cap = cv2.VideoCapture(i)
                
                if cap.isOpened():
                    # Try to read a frame
                    ret, frame = cap.read()
                    
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        
                        # Get camera properties
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        fourcc = cap.get(cv2.CAP_PROP_FOURCC)
                        
                        camera_info = {
                            'index': i,
                            'width': int(width),
                            'height': int(height),
                            'fps': fps,
                            'fourcc': int(fourcc),
                            'backend': cap.getBackendName()
                        }
                        
                        working_cameras.append(camera_info)
                        print(f"✅ SUCCESS - {width}x{height} @ {fps:.1f}fps")
                        
                        # Try to get additional properties
                        try:
                            brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
                            contrast = cap.get(cv2.CAP_PROP_CONTRAST)
                            saturation = cap.get(cv2.CAP_PROP_SATURATION)
                            exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
                            
                            print(f"    Backend: {camera_info['backend']}")
                            print(f"    Properties - Brightness: {brightness}, Contrast: {contrast}")
                            print(f"    Saturation: {saturation}, Exposure: {exposure}")
                        except:
                            pass
                            
                    else:
                        print("❌ FAILED - Could not read frame")
                        
                    cap.release()
                else:
                    print("❌ FAILED - Could not open")
                    
            except Exception as e:
                print(f"❌ ERROR - {e}")
                
        return working_cameras
    
    def test_camera_performance(self, camera_index, duration=5):
        """Test camera performance for a specific duration"""
        print(f"\n⚡ PERFORMANCE TEST - Camera {camera_index} ({duration}s)...")
        print("-" * 50)
        
        try:
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                print(f"❌ Could not open camera {camera_index}")
                return
            
            frame_count = 0
            start_time = datetime.now()
            
            while (datetime.now() - start_time).seconds < duration:
                ret, frame = cap.read()
                if ret:
                    frame_count += 1
                else:
                    print("⚠️  Frame read failed")
                    break
            
            end_time = datetime.now()
            elapsed = (end_time - start_time).total_seconds()
            actual_fps = frame_count / elapsed if elapsed > 0 else 0
            
            print(f"✅ Captured {frame_count} frames in {elapsed:.2f}s")
            print(f"✅ Actual FPS: {actual_fps:.2f}")
            
            cap.release()
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
    
    def check_permissions(self):
        """Check camera permissions"""
        print("\n🔐 CHECKING PERMISSIONS...")
        print("-" * 40)
        
        # Check if user is in video group
        try:
            import grp
            video_group = grp.getgrnam('video')
            current_user = os.getenv('USER', 'unknown')
            
            if current_user in video_group.gr_mem:
                print(f"✅ User '{current_user}' is in 'video' group")
            else:
                print(f"⚠️  User '{current_user}' is NOT in 'video' group")
                print("   Add user to video group: sudo usermod -a -G video $USER")
                
        except Exception as e:
            print(f"⚠️  Could not check video group membership: {e}")
        
        # Check device permissions
        try:
            video_devices = [f'/dev/{d}' for d in os.listdir('/dev') if d.startswith('video')]
            for device in video_devices:
                if os.access(device, os.R_OK):
                    print(f"✅ Read access to {device}")
                else:
                    print(f"❌ No read access to {device}")
        except Exception as e:
            print(f"⚠️  Could not check device permissions: {e}")
    
    def generate_report(self, working_cameras):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("📊 CAMERA TEST REPORT")
        print("=" * 80)
        
        if working_cameras:
            print(f"✅ SUCCESS: Found {len(working_cameras)} working camera(s)")
            print("\n📋 CAMERA DETAILS:")
            
            for cam in working_cameras:
                print(f"\n🎥 Camera Index: {cam['index']}")
                print(f"   Resolution: {cam['width']}x{cam['height']}")
                print(f"   FPS: {cam['fps']:.1f}")
                print(f"   Backend: {cam['backend']}")
                print(f"   FOURCC: {cam['fourcc']}")
                
            # Recommend best camera
            best_camera = max(working_cameras, key=lambda x: x['width'] * x['height'])
            print(f"\n🏆 RECOMMENDED CAMERA: Index {best_camera['index']}")
            print(f"   Best resolution: {best_camera['width']}x{best_camera['height']}")
            
        else:
            print("❌ NO WORKING CAMERAS FOUND")
            print("\n🔧 TROUBLESHOOTING SUGGESTIONS:")
            print("   1. Check if camera is connected properly")
            print("   2. Install camera drivers: sudo apt update && sudo apt install ubuntu-drivers-common")
            print("   3. Install v4l-utils: sudo apt install v4l-utils")
            print("   4. Check USB devices: lsusb")
            print("   5. Restart system after driver installation")
            print("   6. Try different USB ports")
            print("   7. Check dmesg for hardware errors: dmesg | grep -i camera")
        
        print("\n" + "=" * 80)
    
    def run_full_test(self):
        """Run complete camera test suite"""
        self.print_header()
        
        # Check system video devices
        video_devices = self.check_video_devices()
        
        # Check permissions
        self.check_permissions()
        
        # Test OpenCV camera access
        working_cameras = self.test_opencv_cameras()
        
        # Performance test on first working camera
        if working_cameras:
            self.test_camera_performance(working_cameras[0]['index'])
        
        # Generate report
        self.generate_report(working_cameras)
        
        return working_cameras

def main():
    """Main function to run camera tests"""
    try:
        tester = CameraTest()
        working_cameras = tester.run_full_test()
        
        # Exit with appropriate code
        if working_cameras:
            print(f"\n✅ Test completed successfully - {len(working_cameras)} camera(s) available")
            sys.exit(0)
        else:
            print("\n❌ Test completed - No working cameras found")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
