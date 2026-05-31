import cv2
import numpy as np


class WindowManager:
    WINDOWS = ["Live Camera", "Calibrated Board", "Chess State", "Info"]

    def setup(self) -> None:
        for name in self.WINDOWS:
            cv2.namedWindow(name)

    def destroy(self) -> None:
        cv2.destroyAllWindows()

    def set_mouse_callback(self, window: str, callback) -> None:
        cv2.setMouseCallback(window, callback)

    def show(self, frames: dict[str, np.ndarray]) -> None:
        for window, image in frames.items():
            if window in self.WINDOWS:
                cv2.imshow(window, image)

    def wait_key(self, delay: int = 10) -> str | None:
        key = cv2.waitKey(delay) & 0xFF
        if key == 255:
            return None
        return chr(key)

    def is_open(self, window: str) -> bool:
        return cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) >= 1