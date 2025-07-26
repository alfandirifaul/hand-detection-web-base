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
camera = None
try:
    camera = Camera()
    print("Camera initialized successfully")
except Exception as e:
    print(f"Warning: Failed to initialize camera: {e}")
    print("Proceeding with web-only camera mode")

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
    while streaming:
        if camera is not None:
            try:
                frame = camera.get_frame()
                
                # Process the frame with hand detection
                processed_frame, detection_data = handDetector.process_frame(frame)
                
                # Encode the processed frame to JPEG
                ret, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    # Convert to base64 for sending via socketio
                    image_base64 = base64.b64encode(buffer).decode('utf-8')
                    socketio.emit('server_frame', {
                        "image": f'data:image/jpeg;base64,{image_base64}',
                        "detection_data": detection_data
                    })
            except Exception as e:
                print(f"Error in camera stream: {e}")
        
        # Control the frame rate to avoid overwhelming the server
        time.sleep(1/15)  # Target 15 FPS

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_stream')
def handle_start_stream():
    global streaming, stream_thread
    
    if not streaming:
        streaming = True
        stream_thread = threading.Thread(target=camera_stream)
        stream_thread.daemon = True
        stream_thread.start()
        print("Camera streaming started")
        return {"status": "started"}
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
    print("Client connected")
    return {"camera_available": camera is not None}
    
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
