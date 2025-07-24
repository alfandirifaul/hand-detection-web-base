import cv2
import mediapipe as mp
import numpy as np
import time  # Add time module for tracking


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
        
        # Add flag to track if buttons should be shown
        self.show_buttons = False
        
        # Add timestamp for last hand detection
        self.last_hand_detected_time = 0

    def _is_touching(self, finger_pos, button):
        bx, by = button["pos"]
        bw, bh = button["size"]
        fx, fy = finger_pos
        return bx <= fx <= bx + bw and by <= fy <= by + bh
    
    def _count_fingers(self, hand_landmarks):
        # Get fingertip landmarks
        fingertips = [
            self.mp_hands.HandLandmark.THUMB_TIP,
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
            self.mp_hands.HandLandmark.RING_FINGER_TIP,
            self.mp_hands.HandLandmark.PINKY_TIP
        ]
        
        # Get middle knuckle landmarks
        knuckles = [
            self.mp_hands.HandLandmark.THUMB_IP,  # For thumb
            self.mp_hands.HandLandmark.INDEX_FINGER_PIP,
            self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
            self.mp_hands.HandLandmark.RING_FINGER_PIP,
            self.mp_hands.HandLandmark.PINKY_PIP
        ]
        
        # Count extended fingers
        extended_fingers = 0
        for i in range(5):
            # Thumb is handled differently due to its orientation
            if i == 0:
                # Check if thumb is extended based on its position relative to index finger
                if hand_landmarks.landmark[fingertips[i]].x < hand_landmarks.landmark[knuckles[1]].x:
                    extended_fingers += 1
            else:
                # For other fingers, check if fingertip is higher than knuckle
                if hand_landmarks.landmark[fingertips[i]].y < hand_landmarks.landmark[knuckles[i]].y:
                    extended_fingers += 1
                    
        return extended_fingers

    def process_frame(self, frame):
        # Process the frame with MediaPipe first
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True
        
        # Update hand detection status
        if results.multi_hand_landmarks:
            self.show_buttons = True
            self.last_hand_detected_time = time.time()  # Update timestamp
        else:
            # If no hands detected for 5 seconds, hide buttons
            if self.show_buttons and time.time() - self.last_hand_detected_time > 5:
                self.show_buttons = False
                print("No hands detected for 5 seconds - hiding buttons")
        
        # Draw buttons only if they should be shown
        if self.show_buttons:
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

                # Check for button touch (only if buttons are shown)
                if self.show_buttons:
                    if self._is_touching((ix, iy), self.button_left):
                        # Visual feedback - change button color temporarily
                        cv2.rectangle(frame, self.button_left["pos"], 
                            (self.button_left["pos"][0] + self.button_left["size"][0], 
                             self.button_left["pos"][1] + self.button_left["size"][1]), 
                            (255, 255, 255), cv2.FILLED)
                        
                        print(f"Touch detected on {self.button_left['name']} button at ({ix}, {iy})")
                        if self.nodeRedClient:
                            try:
                                self.nodeRedClient.sendData({"button": self.button_left["name"], "action": True})
                                print(f"Data sent to Node-RED: {self.button_left['name']}")
                            except Exception as e:
                                print(f"Error sending data to Node-RED: {e}")
                        else:
                            print("NodeRedClient is not initialized")
                    
                    # Same for right button...
                    if self._is_touching((ix, iy), self.button_right):
                        # Visual feedback - change button color temporarily
                        cv2.rectangle(frame, self.button_right["pos"], 
                            (self.button_right["pos"][0] + self.button_right["size"][0], 
                             self.button_right["pos"][1] + self.button_right["size"][1]), 
                            (255, 255, 255), cv2.FILLED)
                        
                        print(f"Touch detected on {self.button_right['name']} button at ({ix}, {iy})")
                        if self.nodeRedClient:
                            try:
                                self.nodeRedClient.sendData({"button": self.button_right["name"], "action": True})
                                print(f"Data sent to Node-RED: {self.button_right['name']}")
                            except Exception as e:
                                print(f"Error sending data to Node-RED: {e}")
                        else:
                            print("NodeRedClient is not initialized")

        return frame

    def close(self):
        self.hands.close()