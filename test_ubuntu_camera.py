#!/usr/bin/env python3
"""
Ubuntu Camera Debug Script
This script helps diagnose camera issues on Ubuntu servers
"""
import cv2
import os
import sys

def test_camera():
    print("=" * 60)
    print("🎥 UBUNTU CAMERA DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Check system info
    print("\n📊 SYSTEM INFORMATION:")
    try:
        import platform
        print(f"   OS: {platform.system()} {platform.release()}")
        print(f"   Python: {sys.version}")
        print(f"   OpenCV: {cv2.__version__}")
    except Exception as e:
        print(f"   Error getting system info: {e}")
    
    # Check user permissions
    print("\n👤 USER PERMISSIONS:")
    try:
        user_groups = os.popen('groups').read().strip()
        if 'video' in user_groups:
            print("   ✅ User is in 'video' group")
        else:
            print("   ❌ User is NOT in 'video' group")
            print("   🔧 Fix: sudo usermod -a -G video $USER")
    except Exception as e:
        print(f"   Error checking groups: {e}")
    
    # Check video devices
    print("\n📱 VIDEO DEVICES:")
    try:
        video_devices = [d for d in os.listdir('/dev') if d.startswith('video')]
        video_devices.sort()
        if video_devices:
            print(f"   Found devices: {', '.join(video_devices)}")
            for device in video_devices:
                device_path = f"/dev/{device}"
                try:
                    stat_info = os.stat(device_path)
                    permissions = oct(stat_info.st_mode)[-3:]
                    print(f"   {device_path}: permissions {permissions}")
                except Exception as e:
                    print(f"   {device_path}: error {e}")
        else:
            print("   ❌ No /dev/video* devices found!")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test camera indices
    print("\n🔍 TESTING CAMERA INDICES:")
    working_cameras = []
    
    for i in range(5):  # Test first 5 indices
        print(f"\n   Testing index {i}:")
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    backend = cap.getBackendName()
                    
                    print(f"      ✅ Working! {width}x{height} @ {fps:.1f}fps")
                    print(f"      Backend: {backend}")
                    working_cameras.append(i)
                else:
                    print(f"      ❌ Cannot read frames")
                cap.release()
            else:
                print(f"      ❌ Cannot open")
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    if working_cameras:
        print(f"   ✅ Found {len(working_cameras)} working camera(s): {working_cameras}")
        print("   🚀 Your camera should work with the main application!")
    else:
        print("   ❌ No working cameras found!")
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("   1. sudo apt update && sudo apt install v4l-utils")
        print("   2. sudo usermod -a -G video $USER")
        print("   3. Logout and login again")
        print("   4. lsusb | grep -i camera")
        print("   5. v4l2-ctl --list-devices")
        print("   6. sudo chmod 666 /dev/video*")
    print("=" * 60)

if __name__ == "__main__":
    test_camera()
