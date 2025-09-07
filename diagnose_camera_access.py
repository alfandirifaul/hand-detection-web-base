#!/usr/bin/env python3
"""
Quick camera access test - checks if camera is available or if another process is using it
"""
import cv2
import subprocess
import os

def check_camera_processes():
    """Check if any processes are using the camera"""
    print("🔍 CHECKING FOR PROCESSES USING CAMERA")
    print("=" * 50)
    
    try:
        # Check if any process is using /dev/video0
        result = subprocess.run(['lsof', '/dev/video0'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout:
            print("⚠️  Found processes using /dev/video0:")
            print(result.stdout)
            return True
        else:
            print("✅ No processes found using /dev/video0")
            return False
            
    except FileNotFoundError:
        print("⚠️  lsof command not found, trying alternative...")
        
        try:
            # Alternative method using fuser
            result = subprocess.run(['fuser', '/dev/video0'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                print("⚠️  Found processes using /dev/video0:")
                print(result.stdout)
                return True
            else:
                print("✅ No processes found using /dev/video0")
                return False
        except FileNotFoundError:
            print("⚠️  Neither lsof nor fuser available")
            return False

def test_direct_camera_access():
    """Test direct camera access"""
    print("\n🎥 TESTING DIRECT CAMERA ACCESS")
    print("=" * 50)
    
    # Test different backends
    backends = [
        (cv2.CAP_V4L2, "V4L2"),
        (cv2.CAP_ANY, "ANY"),
        (cv2.CAP_GSTREAMER, "GStreamer")
    ]
    
    for backend, name in backends:
        print(f"\n🔍 Testing {name} backend...")
        try:
            cap = cv2.VideoCapture(0, backend)
            
            if cap.isOpened():
                print(f"   ✅ {name}: Camera opened")
                
                # Test frame capture
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"   ✅ {name}: Frame captured successfully ({frame.shape})")
                    cap.release()
                    return True
                else:
                    print(f"   ❌ {name}: Cannot capture frames")
            else:
                print(f"   ❌ {name}: Cannot open camera")
            
            cap.release()
            
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
    
    return False

def kill_camera_processes():
    """Kill processes that might be using the camera"""
    print("\n🔧 ATTEMPTING TO FREE CAMERA")
    print("=" * 50)
    
    try:
        # Kill processes using /dev/video0
        result = subprocess.run(['sudo', 'fuser', '-k', '/dev/video0'], 
                              capture_output=True, text=True)
        print("✅ Attempted to kill processes using /dev/video0")
        
        # Wait a moment for processes to release
        import time
        time.sleep(2)
        
        return True
    except Exception as e:
        print(f"⚠️  Could not kill processes: {e}")
        return False

def main():
    print("🎥 CAMERA ACCESS DIAGNOSTIC")
    print("=" * 60)
    
    # Check if camera device exists
    if not os.path.exists('/dev/video0'):
        print("❌ /dev/video0 does not exist!")
        return
    
    print("✅ /dev/video0 exists")
    
    # Check if processes are using camera
    camera_in_use = check_camera_processes()
    
    # Test direct access
    success = test_direct_camera_access()
    
    if not success and camera_in_use:
        print("\n💡 SOLUTION: Camera appears to be in use by another process")
        print("   Try: sudo fuser -k /dev/video0")
        print("   Or restart your application")
        
        user_input = input("\nDo you want me to try killing camera processes? (y/n): ")
        if user_input.lower() == 'y':
            if kill_camera_processes():
                print("\n🔄 Retesting camera access...")
                success = test_direct_camera_access()
    
    if success:
        print("\n🎉 CAMERA IS ACCESSIBLE!")
        print("   Your camera should work with the main application now.")
    else:
        print("\n❌ CAMERA ACCESS FAILED")
        print("   Additional troubleshooting needed.")

if __name__ == "__main__":
    main()
