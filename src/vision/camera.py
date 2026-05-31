import cv2
import numpy as np
from collections import deque


class Camera:
    RESIZE = (320, 180)

    def __init__(self) -> None:
        self.camera: cv2.VideoCapture
        self.buffer: deque = deque()

    def start_cam(self, cam_id: int, resolution: tuple[int, int], fps: int) -> bool:
        self.camera = cv2.VideoCapture(cam_id if cam_id is not None else 0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.camera.set(cv2.CAP_PROP_FPS, fps)

        if not self.camera.isOpened():
            print("Error: Could not open video.")
            return False

        print("Camera is opened successfully.")
        return True

    def close_cam(self) -> None:
        self.camera.release()

    def capture_frame(self, should_buffer: bool) -> np.ndarray:
        ret, frame = self.camera.read()

        if not ret:
            return None

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if should_buffer:
            self.buffer_frame(frame.copy())

        return frame

    def buffer_frame(self, frame: np.ndarray) -> None:
        frame = cv2.resize(frame, self.RESIZE)
        self.buffer.append(frame)

    def get_latest_frame(self, remove: bool) -> np.ndarray:
        if remove:
            return self.buffer.pop()

        if len(self.buffer) == 0:
            return None

        return self.buffer[-1]

    def get_oldest_frame(self, remove: bool) -> np.ndarray:
        if remove:
            return self.buffer.popleft()

        return self.buffer[0]
