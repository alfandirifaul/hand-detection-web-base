import cv2 as cv

class Camera:
    def __init__(self):
        self.cap = cv.VideoCapture(1)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")

    def openCamera(self):
        if not self.cap.isOpened():
            self.cap.open(1)
            if not self.cap.isOpened():
                raise Exception("Could not open video device")

    def get_frame(self):
        if not self.cap.isOpened():
            raise Exception("Camera is not opened")
        ret, frame = self.cap.read()
        frame = cv.flip(frame, 1)
        if not ret:
            print("Warning: Failed to read frame. Try a different camera index.")
            raise Exception("Could not read frame from video device")

        key = cv.waitKey(1)
        if key == 27:
            print("Exiting...")
            self.release()
            exit(0)

        return frame

    def release(self):
        self.cap.release()
        cv.destroyAllWindows()