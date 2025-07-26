from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import threading
import time
import cv2
import base64
import os

from handDetection import HandDetection
from nodeRedClient import NodeRedClient
from imageProcessing import ImageProcessing
from camera import Camera

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize clients
handDataClient = NodeRedClient(
    nodeRedUrl="http://localhost:1880",
    targetUrl="/hand-detection"
)

# Initialize camera
camera = Camera()
try:
    print("🎥 Attempting to initialize camera on Ubuntu server...")
    print("✅ Camera initialized successfully")
    print(f"📱 Camera status: {'opened' if camera.is_opened() else 'closed'}")
except Exception as e:
    print(f"❌ Warning: Failed to initialize camera: {e}")
    print("🔧 Ubuntu Camera Troubleshooting:")
    print("   1. Check if camera is connected: lsusb | grep -i camera")
    print("   2. Check video devices: ls -la /dev/video*")
    print("   3. Install v4l-utils: sudo apt install v4l-utils")
    print("   4. Check permissions: sudo usermod -a -G video $USER")
    print("   5. Run debug script: python3 ubuntu_camera_debug.py")
    print("🌐 Proceeding with web-only camera mode")

# Initialize hand detector
handDetector = HandDetection(nodeRedClient=handDataClient)

# Init image processing
imageProcessing = ImageProcessing(handDetector)

# Global flag to control camera streaming
streaming = False
stream_thread = None

def camera_stream():
    global streaming
    
    print("Starting camera stream thread")
    frame_count = 0
    
    while streaming:
        if camera is not None:
            try:
                frame = camera.get_frame()
                
                if frame is None:
                    print("Warning: get_frame() returned None")
                    time.sleep(0.1)
                    continue
                
                # Process the frame with hand detection
                processed_frame, detection_data = handDetector.process_frame(frame)
                
                # Encode the processed frame to JPEG
                ret, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    # Convert to base64 for sending via socketio
                    image_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Log frame transmission every 30 frames (roughly every 2 seconds at 15fps)
                    frame_count += 1
                    if frame_count % 30 == 0:
                        print(f"Successfully transmitted frame #{frame_count} to web client")
                    
                    socketio.emit('server_frame', {
                        "image": f'data:image/jpeg;base64,{image_base64}',
                        "detection_data": detection_data
                    })
                else:
                    print("Error: Failed to encode frame to JPEG")
                    
            except Exception as e:
                print(f"Error in camera stream: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("Warning: Camera is None in stream thread")
            break
        
        # Control the frame rate to avoid overwhelming the server
        time.sleep(1/15)  # Target 15 FPS

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_stream')
def handle_start_stream():
    global streaming, stream_thread
    
    print(f"🚀 Received start_stream request")
    print(f"   Current streaming status: {streaming}")
    print(f"   Camera available: {camera is not None}")
    print(f"   Camera opened: {camera.is_opened() if camera else 'N/A'}")
    
    if not streaming:
        if camera is None:
            print("❌ Cannot start stream: Camera not initialized")
            return {"status": "error", "message": "Camera not available"}
        
        if not camera.is_opened():
            print("⚠️  Camera not opened, attempting to open...")
            try:
                camera.openCamera()
                print("✅ Camera opened successfully")
            except Exception as e:
                print(f"❌ Failed to open camera: {e}")
                return {"status": "error", "message": f"Failed to open camera: {e}"}
        
        streaming = True
        stream_thread = threading.Thread(target=camera_stream)
        stream_thread.daemon = True
        stream_thread.start()
        print("✅ Camera streaming started successfully")
        return {"status": "started"}
    else:
        print("⚠️  Stream already running")
        return {"status": "already_running"}

@socketio.on('stop_stream')
def handle_stop_stream():
    global streaming
    streaming = False
    print("Camera streaming stopped")
    return {"status": "stopped"}

@socketio.on('frame')
def handle_client_frame(data):  
    """Handle frames sent from the client's webcam (fallback when server camera isn't available)"""
    try:
        if not streaming or camera is None:
            imageProcessing.handleFrame(data, socketio)
    except Exception as e:
        print(f"Error processing client frame: {e}")

@socketio.on('connect')
def handle_connect():
    print("🔌 Client connected")
    camera_available = camera is not None and camera.is_opened()
    print(f"   📱 Camera available: {camera_available}")
    return {"camera_available": camera_available}
    
@socketio.on('disconnect')
def handle_disconnect():
    global streaming
    if streaming:
        streaming = False
        print("Streaming stopped due to client disconnect")
    
if __name__ == '__main__':
    try:
        print("Starting server at http://0.0.0.0:5050")
        socketio.run(app, host='0.0.0.0', port=5050, debug=True, allow_unsafe_werkzeug=True)
    finally:
        streaming = False
        if camera is not None:
            camera.release()
        handDetector.close()
