#!/usr/bin/env python3
"""
Ubuntu Camera Debug Script
Comprehensive camera testing and troubleshooting for Ubuntu servers
"""

import cv2
import os
import subprocess
import sys
import time

def print_header(title):
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def check_system_info():
    print_header("SYSTEM INFORMATION")
    
    try:
        # Check Ubuntu version
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('PRETTY_NAME'):
                    os_name = line.split('=')[1].strip().strip('"')
                    print(f"OS: {os_name}")
                    break
    except:
        print("OS: Unknown")
    
    # Check Python and OpenCV versions
    print(f"Python: {sys.version.split()[0]}")
    print(f"OpenCV: {cv2.__version__}")
    
    # Check if running in a container
    if os.path.exists('/.dockerenv'):
        print("🐳 Running in Docker container")
    
    # Check user groups
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True)
        groups = result.stdout.strip()
        if 'video' in groups:
            print("✅ User is in 'video' group")
        else:
            print("❌ User is NOT in 'video' group")
            print("   Fix: sudo usermod -a -G video $USER")
    except:
        print("⚠️  Could not check user groups")

def check_video_devices():
    print_header("VIDEO DEVICES IN /dev/")
    
    try:
        video_devices = [d for d in os.listdir('/dev') if d.startswith('video')]
        video_devices.sort()
        
        if video_devices:
            print(f"Found {len(video_devices)} video device(s):")
            for device in video_devices:
                device_path = f"/dev/{device}"
                try:
                    # Check permissions
                    stat_info = os.stat(device_path)
                    permissions = oct(stat_info.st_mode)[-3:]
                    print(f"  📹 {device_path} (permissions: {permissions})")
                except Exception as e:
                    print(f"  📹 {device_path} (error reading: {e})")
        else:
            print("❌ No video devices found in /dev/")
            print("   Try: sudo apt install v4l-utils")
            print("   Then: v4l2-ctl --list-devices")
    except Exception as e:
        print(f"❌ Error accessing /dev/: {e}")

def check_v4l_devices():
    print_header("V4L2 DEVICE INFORMATION")
    
    try:
        # Check if v4l2-ctl is available
        result = subprocess.run(['which', 'v4l2-ctl'], capture_output=True)
        if result.returncode != 0:
            print("❌ v4l2-ctl not found")
            print("   Install: sudo apt install v4l-utils")
            return
        
        # List video devices
        print("📋 Listing video devices:")
        result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                              capture_output=True, text=True, timeout=10)
        if result.stdout:
            print(result.stdout)
        else:
            print("No devices found or command failed")
            
    except subprocess.TimeoutExpired:
        print("⚠️  v4l2-ctl command timed out")
    except Exception as e:
        print(f"❌ Error running v4l2-ctl: {e}")

def test_opencv_cameras():
    print_header("OPENCV CAMERA TESTING")
    
    working_cameras = []
    
    for i in range(10):
        print(f"\n🔍 Testing camera index {i}...")
        
        try:
            cap = cv2.VideoCapture(i)
            
            if not cap.isOpened():
                print(f"❌ Camera {i}: Cannot open")
                continue
            
            # Get initial properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            backend = cap.getBackendName()
            
            print(f"📊 Camera {i} properties:")
            print(f"   Backend: {backend}")
            print(f"   Default resolution: {width}x{height}")
            print(f"   Default FPS: {fps:.1f}")
            
            # Test frame capture
            print(f"📸 Testing frame capture...")
            ret, frame = cap.read()
            
            if ret and frame is not None:
                actual_shape = frame.shape
                print(f"✅ Frame captured: {actual_shape[1]}x{actual_shape[0]} (HxW)")
                
                # Test multiple frame captures
                success_count = 0
                for test_frame in range(5):
                    ret, _ = cap.read()
                    if ret:
                        success_count += 1
                    time.sleep(0.1)
                
                print(f"📈 Frame capture success rate: {success_count}/5")
                
                if success_count >= 3:
                    working_cameras.append({
                        'index': i,
                        'backend': backend,
                        'resolution': f"{width}x{height}",
                        'fps': fps,
                        'device_path': f"/dev/video{i}"
                    })
                    print(f"✅ Camera {i} is WORKING")
                else:
                    print(f"⚠️  Camera {i} has unstable frame capture")
            else:
                print(f"❌ Camera {i}: Cannot capture frames")
            
            cap.release()
            
        except Exception as e:
            print(f"❌ Camera {i}: Error - {e}")
    
    return working_cameras

def show_troubleshooting_tips():
    print_header("TROUBLESHOOTING TIPS")
    
    tips = [
        "📦 Install camera utilities:",
        "   sudo apt update",
        "   sudo apt install v4l-utils uvcdynctrl",
        "",
        "👥 Add user to video group:",
        "   sudo usermod -a -G video $USER",
        "   # Then logout and login again",
        "",
        "🔍 Check USB cameras:",
        "   lsusb | grep -i camera",
        "   lsusb | grep -i video",
        "",
        "🔧 Camera permissions:",
        "   ls -la /dev/video*",
        "   # Should show crw-rw---- with video group",
        "",
        "🐳 For Docker containers:",
        "   docker run --device=/dev/video0 your_image",
        "   # Or use --privileged flag",
        "",
        "⚡ Performance optimization:",
        "   # Use MJPEG format for better performance",
        "   cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))",
        "   # Reduce buffer size for lower latency",
        "   cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)",
    ]
    
    for tip in tips:
        print(tip)

def main():
    print("🎥 Ubuntu Camera Debug Tool")
    print("This script will help diagnose camera issues on Ubuntu servers")
    
    check_system_info()
    check_video_devices()
    check_v4l_devices()
    
    working_cameras = test_opencv_cameras()
    
    if working_cameras:
        print_header("WORKING CAMERAS SUMMARY")
        print(f"Found {len(working_cameras)} working camera(s):")
        
        for cam in working_cameras:
            print(f"\n🎥 Camera {cam['index']}:")
            print(f"   Device: {cam['device_path']}")
            print(f"   Backend: {cam['backend']}")
            print(f"   Resolution: {cam['resolution']}")
            print(f"   FPS: {cam['fps']:.1f}")
        
        print_header("RECOMMENDED CAMERA CONFIGURATION")
        best_camera = working_cameras[0]
        print(f"🎯 Use camera index: {best_camera['index']}")
        print(f"📱 Device path: {best_camera['device_path']}")
        print(f"🔧 Backend: {best_camera['backend']}")
        print(f"\n📝 Python code to use:")
        print(f"   cap = cv2.VideoCapture({best_camera['index']})")
        print(f"   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)")
        print(f"   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)")
        print(f"   cap.set(cv2.CAP_PROP_FPS, 15)")
        print(f"   cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))")
        
    else:
        print_header("NO WORKING CAMERAS FOUND")
        print("❌ No cameras could capture frames successfully")
        show_troubleshooting_tips()

if __name__ == "__main__":
    main()
