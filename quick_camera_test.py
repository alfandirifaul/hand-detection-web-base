#!/usr/bin/env python3
"""
Quick Camera Port Detection Script
Simple script to quickly find available camera ports on Ubuntu server.
"""

import cv2
import os

def find_camera_ports(max_test=10):
    """
    Find all available camera ports
    """
    print("🔍 Scanning for available cameras...")
    print("-" * 40)
    
    available_ports = []
    
    # Check /dev/video* devices first
    try:
        video_devices = [d for d in os.listdir('/dev') if d.startswith('video')]
        video_devices.sort()
        if video_devices:
            print(f"📱 Video devices found in /dev/: {', '.join(video_devices)}")
    except:
        print("⚠️  Could not access /dev/ directory")
    
    # Test OpenCV camera access
    print(f"\n🧪 Testing camera indices 0-{max_test-1}...")
    
    for port in range(max_test):
        try:
            cap = cv2.VideoCapture(port)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    available_ports.append({
                        'port': port,
                        'width': width,
                        'height': height,
                        'fps': fps
                    })
                    
                    print(f"✅ Camera {port}: {width}x{height} @ {fps:.1f}fps")
                else:
                    print(f"❌ Camera {port}: Failed to read frame")
                cap.release()
            else:
                print(f"❌ Camera {port}: Could not open")
        except Exception as e:
            print(f"❌ Camera {port}: Error - {e}")
    
    return available_ports

def main():
    print("=" * 50)
    print("🎥 QUICK CAMERA PORT DETECTION")
    print("=" * 50)
    
    cameras = find_camera_ports()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    
    if cameras:
        print(f"✅ Found {len(cameras)} working camera(s):")
        for cam in cameras:
            print(f"   🎥 Port {cam['port']}: {cam['width']}x{cam['height']} @ {cam['fps']:.1f}fps")
        
        # Show recommended port
        best_cam = max(cameras, key=lambda x: x['width'] * x['height'])
        print(f"\n🏆 RECOMMENDED PORT: {best_cam['port']}")
        print(f"   Best resolution: {best_cam['width']}x{best_cam['height']}")
        
        # Show usage example
        print(f"\n💡 USAGE IN CODE:")
        print(f"   camera = cv2.VideoCapture({best_cam['port']})")
        
    else:
        print("❌ No working cameras found!")
        print("\n🔧 Try these commands:")
        print("   sudo apt update")
        print("   sudo apt install v4l-utils")
        print("   v4l2-ctl --list-devices")
        print("   lsusb  # Check USB devices")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
