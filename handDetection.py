import cv2
import mediapipe as mp
import numpy as np


class HandDetection:
    def __init__(self, nodeRedClient=None):
        # Initialize MediaPipe Hands solution
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Store Node-Red Client
        self.nodeRedClient = nodeRedClient

        # Button definitions
        self.button_left = {"pos": (50, 50), "size": (100, 50), "color": (0, 255, 0), "name": "green"}
        self.button_right = {"pos": (490, 50), "size": (100, 50), "color": (0, 0, 255), "name": "red"}

    def _is_touching(self, finger_pos, button):
        bx, by = button["pos"]
        bw, bh = button["size"]
        fx, fy = finger_pos
        return bx <= fx <= bx + bw and by <= fy <= by + bh

    def process_frame(self, frame):
        # Draw buttons
        cv2.rectangle(
            frame, 
            self.button_left["pos"], 
            (
                self.button_left["pos"][0] + self.button_left["size"][0], 
                self.button_left["pos"][1] + self.button_left["size"][1]), 
                self.button_left["color"], 
                cv2.FILLED
            )
        cv2.rectangle(
            frame, 
            self.button_right["pos"], 
            (
                self.button_right["pos"][0] + self.button_right["size"][0], 
                self.button_right["pos"][1] + self.button_right["size"][1]
            ), 
            self.button_right["color"], 
            cv2.FILLED
        )

        # Convert BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        # Process the frame with MediaPipe
        results = self.hands.process(rgb_frame)

        rgb_frame.flags.writeable = True

        # Data to send to Node-Red
        handData = []

        # Draw hand landmarks on the frame
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

                # Add additional information
                h, w, _ = frame.shape
                
                # Get index finger tip position
                index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                ix, iy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

                # Check for button touch
                if self._is_touching((ix, iy), self.button_left):
                    if self.nodeRedClient:
                        self.nodeRedClient.sendData({"button": self.button_left["name"], "action": "touch"})
                
                if self._is_touching((ix, iy), self.button_right):
                    if self.nodeRedClient:
                        self.nodeRedClient.sendData({"button": self.button_right["name"], "action": "touch"})

        return frame

    def close(self):
        self.hands.close()