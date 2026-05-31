import cv2
import numpy as np


class Calibration:

    BOARD_SIZE = 800
    GRID_SIZE = 8
    FIELD_SIZE = BOARD_SIZE // GRID_SIZE
    CENTER_PATCH_SIZE = 20

    DESTINATION_POINTS = np.float32([
        [0, 0],
        [BOARD_SIZE, 0],
        [BOARD_SIZE, BOARD_SIZE],
        [0, BOARD_SIZE]
    ])

    def __init__(self, top_left: tuple[int, int], top_right: tuple[int, int], bottom_right: tuple[int, int], bottom_left: tuple[int, int]) -> None:
        self.source_points = np.float32([
            top_left,
            top_right,
            bottom_right,
            bottom_left
        ])

        self.matrix = cv2.getPerspectiveTransform(
            self.source_points,
            self.DESTINATION_POINTS
        )

    def warp(self, frame: np.ndarray) -> np.ndarray:
        return cv2.warpPerspective(
            frame,
            self.matrix,
            (self.BOARD_SIZE, self.BOARD_SIZE)
        )

    def get_field(self, warped: np.ndarray, col: int, row: int) -> np.ndarray:
        x1 = col * self.FIELD_SIZE
        y1 = row * self.FIELD_SIZE
        x2 = x1 + self.FIELD_SIZE
        y2 = y1 + self.FIELD_SIZE

        return warped[y1:y2, x1:x2]

    def get_field_name(self, col: int, row: int) -> str:
        files = "abcdefgh"
        file = files[col]
        rank = str(8 - row)

        return f"{file}{rank}"

    def iter_fields(self):
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                yield {
                    "row": row,
                    "col": col,
                    "name": self.get_field_name(col, row)
                }

    def get_field_center(self, col: int, row: int) -> tuple[int, int]:
        x = int(col * self.FIELD_SIZE + self.FIELD_SIZE / 2)
        y = int(row * self.FIELD_SIZE + self.FIELD_SIZE / 2)

        return x, y

    def get_center_patch(self, warped: np.ndarray, col: int, row: int, patch_size: int | None = None) -> np.ndarray:
        if patch_size is None:
            patch_size = self.CENTER_PATCH_SIZE

        center_x, center_y = self.get_field_center(col, row)
        half = patch_size // 2

        x1 = max(center_x - half, 0)
        y1 = max(center_y - half, 0)
        x2 = min(center_x + half, warped.shape[1])
        y2 = min(center_y + half, warped.shape[0])

        return warped[y1:y2, x1:x2]

    def sample_board_signatures(self, warped: np.ndarray) -> dict[str, dict]:
        signatures = {}

        for field in self.iter_fields():
            row = field["row"]
            col = field["col"]
            name = field["name"]
            patch = self.get_center_patch(warped, col, row)
            signature = self.get_center_signature(patch)

            signatures[name] = {
                "row": row,
                "col": col,
                "name": name,
                "center": self.get_field_center(col, row),
                "signature": signature
            }

        return signatures

    @staticmethod
    def get_center_signature(patch: np.ndarray) -> np.ndarray:
        if patch.size == 0:
            return np.zeros(7, dtype=np.float32)

        hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)

        mean_bgr = np.mean(patch, axis=(0, 1))
        mean_hsv = np.mean(hsv, axis=(0, 1))
        mean_gray = np.mean(gray)

        return np.array([*mean_bgr, *mean_hsv, mean_gray], dtype=np.float32)

    @staticmethod
    def field_difference(signature1: np.ndarray, signature2: np.ndarray) -> float:
        return float(np.linalg.norm(signature1 - signature2))

    @staticmethod
    def field_changed(signature1: np.ndarray, signature2: np.ndarray, threshold: float = 30.0) -> bool:
        score = Calibration.field_difference(signature1, signature2)
        return score > threshold

    def detect_changed_fields(self, previous_signatures: dict[str, dict], current_signatures: dict[str, dict], threshold: float = 30.0) -> list[dict]:
        changed_fields = []

        for field in self.iter_fields():
            name = field["name"]
            old = previous_signatures.get(name)
            current = current_signatures.get(name)

            if old is None or current is None:
                continue

            score = self.field_difference(old["signature"], current["signature"])

            if score > threshold:
                changed_fields.append({
                    "name": name,
                    "row": field["row"],
                    "col": field["col"],
                    "score": round(score, 2),
                    "center": current["center"]
                })

        changed_fields.sort(key=lambda entry: entry["score"], reverse=True)
        return changed_fields
