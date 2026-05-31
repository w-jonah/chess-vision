import cv2
import numpy as np

from vision.camera import Camera
from vision.calibration import Calibration
from ui.renderer import BoardRenderer
from ui.window_manager import WindowManager


class CalibrationUI:
    HINT_CONNECTED = "Klicke die 4 Ecken des leeren Brettes im Uhrzeigersinn"
    HINT_QUIT      = "Taste 'q': Beenden"

    def __init__(self, cam: Camera, windows: WindowManager) -> None:
        self._cam     = cam
        self._windows = windows
        self._points: list[tuple[int, int]] = []

    def _mouse_callback(self, event, x, y, flags, param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN and len(self._points) < 4:
            self._points.append((x, y))

    def run(self) -> Calibration | None:
        self._windows.set_mouse_callback("Live Camera", self._mouse_callback)

        while True:
            frame = self._cam.capture_frame(False)
            if frame is None:
                continue

            display = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            display = BoardRenderer.annotate_points(display, self._points)
            cv2.putText(display, self.HINT_CONNECTED, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display, self.HINT_QUIT, (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 180, 180), 1)

            self._windows.show({"Live Camera": display})
            key = self._windows.wait_key()

            if key == "q":
                return None

            if len(self._points) == 4:
                p = self._points
                return Calibration(p[0], p[1], p[2], p[3])