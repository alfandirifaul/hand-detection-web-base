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
        self.button_left = {"pos": (490, 50), "size": (100, 50), "color": (0, 255, 0), "name": "green"}
        self.button_right = {"pos": (50, 50), "size": (100, 50), "color": (0, 0, 255), "name": "red"}
        
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
        # Flip the frame
        frame = cv2.flip(frame, 1)

        # Data to send to Node-Red
        detection_data = {
            "num_hands": 0,
            "hands": [],
            "fingers_count": 0,
            "buttons_active": self.show_buttons,
            "touched_button": None
        }

        # Process the frame with MediaPipe first
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True
        
        # Variables to track finger counts
        total_fingers = 0
        five_finger_detected = False
        any_fingers_detected = False
        
        # Draw hand landmarks on the frame and count fingers
        if results.multi_hand_landmarks:
            detection_data["num_hands"] = len(results.multi_hand_landmarks)
            
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Count fingers for this hand
                finger_count = self._count_fingers(hand_landmarks)
                total_fingers += finger_count
                
                # Check if this hand has 5 fingers extended
                if finger_count == 5:
                    five_finger_detected = True
                
                # Check if any fingers are detected
                if finger_count > 0:
                    any_fingers_detected = True
        
            # Store hand data
            hand_data = {
                "id": hand_idx,
                "fingers": finger_count
            }
            detection_data["hands"].append(hand_data)
            
            # Display finger count near the hand
            h, w, _ = frame.shape
            wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
            wrist_x, wrist_y = int(wrist.x * w), int(wrist.y * h)
            
            # Draw the finger count near the wrist
            cv2.putText(
                frame, 
                f"Fingers: {finger_count}", 
                (wrist_x - 10, wrist_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (255, 255, 255), 
                2
            )
            
            # Display hand coordinates at the right bottom but above the text
            index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            ix, iy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            
            # Position the coordinates display at the right bottom
            coords_text_x = f"X: {ix}"
            coords_text_y = f"Y: {iy}"

            # Get the size of both text lines to determine the background rectangle dimensions
            (x_width, x_height), _ = cv2.getTextSize(
                coords_text_x,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                1
            )
            (y_width, y_height), _ = cv2.getTextSize(
                coords_text_y,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                1
            )

            # Calculate the maximum width needed
            max_width = max(x_width, y_width)
            total_height = x_height + y_height + 5  # 5 pixels spacing between lines

            # Place at right bottom, above the instruction text
            coords_x = w - max_width - 50  # 10 pixels from right edge
            coords_y_first_line = h - 100  # First line position
            coords_y_second_line = coords_y_first_line + x_height + 5  # Second line position

            # Draw background for better visibility
            cv2.rectangle(
                frame,
                (coords_x - 5, coords_y_first_line - x_height - 5),
                (coords_x + max_width + 5, coords_y_second_line + 5),
                (0, 0, 0, 128),
                cv2.FILLED
            )

            # Draw the coordinates text (X on first line, Y on second line)
            cv2.putText(
                frame,
                coords_text_x,
                (coords_x, coords_y_first_line),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (100, 255, 255),  # Yellow-cyan color for visibility
                1
            )

            cv2.putText(
                frame,
                coords_text_y,
                (coords_x, coords_y_second_line),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (100, 255, 255),  # Yellow-cyan color for visibility
                1
            )
            
            # Draw hand landmarks
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
    
            # Update button visibility based on detection
            if not self.show_buttons and five_finger_detected:
                # Only activate buttons if 5 fingers are detected and buttons are not already active
                self.show_buttons = True
                print("5 fingers detected - showing buttons")
                
            if any_fingers_detected:
                # Update the timestamp as long as any fingers are detected
                self.last_hand_detected_time = time.time()
    
        # If no fingers detected for 5 seconds, hide buttons
        if self.show_buttons and time.time() - self.last_hand_detected_time > 5:
            self.show_buttons = False
            print("No fingers detected for 5 seconds - hiding buttons")
    
        # Store total finger count
        detection_data["fingers_count"] = total_fingers
        detection_data["buttons_active"] = self.show_buttons
        
        # Draw buttons only if they should be shown
        if self.show_buttons:
            # Add a visual cue for button status
            text = "Buttons Enabled - Hide hands for 5s to deactivate"
            # Get the size of the text to properly center it
            (text_width, text_height), baseline = cv2.getTextSize(
                text,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                2
            )
            # Calculate center position
            text_x = (frame.shape[1] - text_width) // 2
            text_y = frame.shape[0] - 30
            
            cv2.putText(
                frame,
                text,
                (text_x, text_y),  
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            
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
        else:
            # Show instruction when buttons aren't visible
            text = "Show 5 fingers to activate buttons"
            # Get the size of the text to properly center it
            (text_width, text_height), baseline = cv2.getTextSize(
                text,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                2
            )
            # Calculate center position
            text_x = (frame.shape[1] - text_width) // 2
            text_y = frame.shape[0] - 30
            
            cv2.putText(
                frame,
                text,
                (text_x, text_y),  
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (200, 200, 200),
                2
            )

        # Process button touches if buttons are active
        if self.show_buttons and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                h, w, _ = frame.shape
                
                # Get index finger tip position
                index_finger_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                ix, iy = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                
                # Check for button touch
                if self._is_touching((ix, iy), self.button_left):
                    # Visual feedback - change button color temporarily
                    cv2.rectangle(frame, self.button_left["pos"], 
                        (self.button_left["pos"][0] + self.button_left["size"][0], 
                         self.button_left["pos"][1] + self.button_left["size"][1]), 
                        (255, 255, 255), cv2.FILLED)
                    
                    finger_count = self._count_fingers(hand_landmarks)
                    print(f"Touch detected on {self.button_left['name']} button at ({ix}, {iy})")
                    detection_data["touched_button"] = self.button_left["name"]
                    if self.nodeRedClient:
                        try:
                            self.nodeRedClient.sendData({"button": self.button_left["name"], "action": True, "fingers": finger_count})
                            print(f"Data sent to Node-RED: {self.button_left['name']} with {finger_count} fingers")
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
                    
                    finger_count = self._count_fingers(hand_landmarks)
                    print(f"Touch detected on {self.button_right['name']} button at ({ix}, {iy})")
                    detection_data["touched_button"] = self.button_right["name"]
                    if self.nodeRedClient:
                        try:
                            self.nodeRedClient.sendData({"button": self.button_right["name"], "action": True, "fingers": finger_count})
                            print(f"Data sent to Node-RED: {self.button_right['name']} with {finger_count} fingers")
                        except Exception as e:
                            print(f"Error sending data to Node-RED: {e}")
                    else:
                        print("NodeRedClient is not initialized")

        return frame, detection_data

    def close(self):
        self.hands.close()