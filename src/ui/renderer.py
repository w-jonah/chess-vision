import cv2
import numpy as np
import chess


class BoardRenderer:
    LIGHT_SQUARE = (235, 209, 166)
    DARK_SQUARE  = (120, 80, 40)
    GRID_COLOR   = (0, 255, 0)
    INFO_BG      = 35
    INFO_FG      = (220, 220, 220)

    @staticmethod
    def draw_grid(image: np.ndarray, grid: int = 8) -> np.ndarray:
        overlay = image.copy()
        step = image.shape[0] // grid
        for i in range(grid + 1):
            x = i * step
            y = i * step
            cv2.line(overlay, (x, 0), (x, image.shape[0]), BoardRenderer.GRID_COLOR, 1)
            cv2.line(overlay, (0, y), (image.shape[1], y), BoardRenderer.GRID_COLOR, 1)
        return overlay

    @staticmethod
    def render_chess_board(board: chess.Board, size: int = 520) -> np.ndarray:
        square = size // 8
        image = np.full((size, size, 3), 245, dtype=np.uint8)

        for rank in range(8):
            for file in range(8):
                tl = (file * square, rank * square)
                br = ((file + 1) * square, (rank + 1) * square)
                is_light = (file + rank) % 2 == 0
                color = BoardRenderer.LIGHT_SQUARE if is_light else BoardRenderer.DARK_SQUARE
                cv2.rectangle(image, tl, br, color, -1)
                cv2.rectangle(image, tl, br, (0, 0, 0), 1)

                idx = chess.square(file, 7 - rank)
                piece = board.piece_at(idx)
                if piece:
                    text = piece.symbol()
                    fs, th = 1.4, 2
                    (tw, teh), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fs, th)
                    tx = tl[0] + (square - tw) // 2
                    ty = tl[1] + (square + teh) // 2
                    text_color = (0, 0, 0) if is_light else (255, 255, 255)
                    cv2.putText(image, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, fs, text_color, th, cv2.LINE_AA)

        return image

    @staticmethod
    def draw_info_panel(lines: list[str], width: int = 600, height: int = 420) -> np.ndarray:
        panel = np.full((height, width, 3), BoardRenderer.INFO_BG, dtype=np.uint8)
        y = 30
        for line in lines:
            cv2.putText(panel, line, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, BoardRenderer.INFO_FG, 1, cv2.LINE_AA)
            y += 28
        return panel

    @staticmethod
    def annotate_points(image: np.ndarray, points: list[tuple[int, int]]) -> np.ndarray:
        annotated = image.copy()
        for idx, point in enumerate(points, start=1):
            cv2.circle(annotated, point, 7, (0, 0, 255), -1)
            cv2.putText(annotated, str(idx), (point[0] + 8, point[1] - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
        return annotated