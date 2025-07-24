import cv2 as cv
import base64
import numpy as np
from handDetection import HandDetection

class ImageProcessing:
    def __init__(self, handDetector: HandDetection):
        self.handDetector = handDetector

    def handleFrame(self, data, socketIo):
        # Decode base64 image
        imageData = data.split(',')[1]
        imageBytes = base64.b64decode(imageData)
        npArr = np.frombuffer(imageBytes, np.uint8)
        frame = cv.imdecode(npArr, cv.IMREAD_COLOR)

        # Process frame with hand detector
        processedFrame = self.handDetector.process_frame(frame)

        # Encode processed frame to send back
        ret, buffer = cv.imencode(
            '.jpg', 
            processedFrame,
            [
                cv.IMWRITE_JPEG_QUALITY, 
                90
            ]
        )

        if ret:
            processedImage = base64.b64encode(buffer).decode('utf-8')
            socketIo.emit('processed_frame', f'data:image/jpeg;base64,{processedImage}')

