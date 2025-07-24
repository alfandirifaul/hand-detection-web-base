from camera import Camera
from handDetection import HandDetection
from nodeRedClient import NodeRedClient
from serialClient import SerialClient

import cv2 as cv
import json
import base64

def main():
    clientUrl = "http://localhost:1880"
    clientSerial = "/dev/tty.usbserial-0001"

    cam = Camera()
    cam.openCamera()

    videoClient = NodeRedClient(
        nodeRedUrl=clientUrl,
        targetUrl="/hand-detection-video"
    )

    handDataClient = NodeRedClient(
        nodeRedUrl=clientUrl,
        targetUrl="/hand-detection",
    )

    serialClient = SerialClient(
        port=clientSerial,
        baudrate=115200,
        timeout=1
    )

    handDetector = HandDetection(nodeRedClient=handDataClient)

    count = 0
    flag = 0
    try:
        while True:
            flag += 1

            if flag > 100:
                serialClient.sendData(str(count))
                count += 1
                flag = 0

            frame = cam.get_frame()
            processedFrame = handDetector.process_frame(frame)

            ret, buffer = cv.imencode(
                '.jpg',
                processedFrame,
                [cv.IMWRITE_JPEG_QUALITY, 90]
            )

            if ret:
                jpgAsText = base64.b64encode(buffer).decode('utf-8')

                videoClient.sendHandData({"image": jpgAsText})

            # cv.imshow("frame", processedFrame)
    finally:
        handDetector.close()
        cam.release()
        serialClient.close()

if __name__ == '__main__':
    main()