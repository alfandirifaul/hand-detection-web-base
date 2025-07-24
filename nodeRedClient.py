import requests
import json
import time
from threading import Thread

from numpy.distutils.conv_template import header


class NodeRedClient:
    def __init__(self, nodeRedUrl="http://localhost:1880", targetUrl="", sendInterval=0.1):
        self.nodeRedUrl = nodeRedUrl + targetUrl
        self.lastSentTime = 0
        self.sendInterval = sendInterval

    def sendData(self, data):
        if not data:
            print("No data to send")
            return

        currentTime = time.time()
        if (currentTime - self.lastSentTime) > self.sendInterval:
            self.lastSentTime = currentTime
            payload = {
                "timestamp": currentTime,
                "data": data
            }
            Thread(target=self._sendRequest, args=(payload,)).start()

    def sendHandData(self, data):
        if not data:
            print("No data to send")
            return

        currentTime = time.time()
        if (currentTime - self.lastSentTime) > self.sendInterval:
            self.lastSentTime = currentTime
            payload = {
                "timestamp": currentTime,
                "data": data
            }

            payload = data

            Thread(target=self._sendRequest, args=(payload,)).start()

    def _sendRequest(self, payload):
        try:
            response = requests.post(
                self.nodeRedUrl,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=0.5
            )

            if response.status_code == 200:
                print("Sent successfully")
                pass
            else:
                print("Failed to send")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")