from flask import Flask, render_template
from flask_socketio import SocketIO

from handDetection import HandDetection
from nodeRedClient import NodeRedClient
from imageProcessing import ImageProcessing

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize clients
handDataClient = NodeRedClient(
    nodeRedUrl="http://localhost:1880",
    targetUrl="/hand-detection"
)

# Initialize hand detector
handDetector = HandDetection(nodeRedClient=handDataClient)

# Init image processing
imageProcessing = ImageProcessing(handDetector)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('frame')
def handle_frame(data):  
    try:
        imageProcessing.handleFrame(data, socketio)
    except Exception as e:
        print(f"Error processing frame: {e}")
    
if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5050, debug=True)
    finally:
        handDetector.close()
