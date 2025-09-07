#!/usr/bin/env python3
"""
Quick camera test to verify the Camera class works properly
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from camera import Camera

def test_camera_class():
    print("🧪 TESTING CAMERA CLASS")
    print("=" * 50)
    
    try:
        # Initialize camera
        print("1. Initializing Camera class...")
        camera = Camera()
        
        # Check if camera is opened
        print("2. Checking if camera is opened...")
        is_opened = camera.is_opened()
        print(f"   Camera opened: {is_opened}")
        
        if is_opened:
            # Test frame capture
            print("3. Testing frame capture...")
            frame = camera.get_frame()
            
            if frame is not None:
                print(f"   ✅ Frame captured successfully: {frame.shape}")
                
                # Test multiple frame captures
                print("4. Testing multiple frame captures...")
                success_count = 0
                for i in range(5):
                    test_frame = camera.get_frame()
                    if test_frame is not None:
                        success_count += 1
                
                print(f"   Success rate: {success_count}/5 frames")
                
                if success_count >= 4:
                    print("\n🎉 CAMERA TEST PASSED!")
                    print("The camera should work with the server now.")
                else:
                    print("\n⚠️  CAMERA TEST PARTIALLY FAILED")
                    print("Camera works but is unstable.")
            else:
                print("   ❌ Failed to capture frame")
                print("\n❌ CAMERA TEST FAILED")
        else:
            print("   ❌ Camera not opened")
            print("\n❌ CAMERA TEST FAILED")
            
        # Clean up
        print("\n5. Releasing camera...")
        camera.release()
        print("   Camera released successfully")
        
    except Exception as e:
        print(f"\n❌ CAMERA TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_camera_class()
