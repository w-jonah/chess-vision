import cv2
import chess

from vision.camera import Camera
from vision.calibration import Calibration
from vision.move_detector import MoveDetector

from ui.renderer import BoardRenderer
from ui.window_manager import WindowManager

from platform.base import ChessPlatform

class GameSession:
    def __init__(self, cam: Camera, calibration: Calibration, windows: WindowManager, platform: ChessPlatform | None = None) -> None:
        self._cam = cam
        self._calibration = calibration
        self._windows = windows
        self._platform = platform

        self._board = None
        self._reference_sigs = None
        self._previous_sigs = None
        self._last_move_text = "Kein Zug erkannt"
        self._changed_fields: list = []
        self._waiting_for_board_update = False


    def _capture_reference(self) -> None:
        """Nimmt ein Referenzbild auf und setzt den Spielstand zurück."""
        frame = self._cam.capture_frame(should_buffer=False)
        warped = self._calibration.warp(frame)
        sigs = self._calibration.sample_board_signatures(warped)
        self._reference_sigs = sigs
        self._previous_sigs = sigs
        if self._board is None:
            self._board = chess.Board()
        self._changed_fields = []
        self._last_move_text = "Startposition initialisiert"


    def _handle_new_photo(self) -> None:
        """Taste 'n': neues Foto aufnehmen und Zug erkennen."""
        frame = self._cam.capture_frame(False)
        warped = self._calibration.warp(frame)
        current_sigs = self._calibration.sample_board_signatures(warped)

        if self._waiting_for_board_update:
            self._previous_sigs = current_sigs
            self._waiting_for_board_update = False
            self._last_move_text = "Brett aktualisiert – du bist dran"
            self._changed_fields = []
            return
 
        self._changed_fields = self._calibration.detect_changed_fields(
            self._previous_sigs, current_sigs
        )
 
        if not self._changed_fields:
            self._last_move_text = "Keine Veränderung erkannt"
            return
 
        changed_names = [f["name"] for f in self._changed_fields]
        move_uci = MoveDetector.detect_move(self._board, changed_names)
 
        if not move_uci:
            self._last_move_text = "Kein eindeutiger Zug gefunden"
            return
 
        self._board.push_uci(move_uci)
        self._previous_sigs  = current_sigs
        self._last_move_text = f"Dein Zug: {move_uci}"
 
        if self._platform is None:
            return
 
        self._platform.submit_move(move_uci)
        ai_move = self._platform.get_opponent_move()
 
        if ai_move:
            self._board.push_uci(ai_move)
            self._last_move_text           = f"Dein Zug: {move_uci}  |  KI: {ai_move} – bitte nachziehen, dann 'n'"
            self._waiting_for_board_update = True
        else:
            self._last_move_text = f"Dein Zug: {move_uci}  |  KI hat nicht geantwortet"

    def _handle_reset(self) -> None:
        """Taste 's': Referenz neu setzen."""
        input("Brett in gewünschten Zustand legen und ENTER drücken...")
        self._capture_reference()
        self._last_move_text = "Referenz neu gesetzt"


    def _build_frames(self, frame, warped) -> dict:
        warped_bgr = cv2.cvtColor(warped, cv2.COLOR_RGB2BGR)
        warped_overlay = BoardRenderer.draw_grid(warped_bgr)
        board_image = BoardRenderer.render_chess_board(self._board)
        info_lines = self._build_info_lines()
        info_panel = BoardRenderer.draw_info_panel(info_lines)

        return {
            "Live Camera":     cv2.cvtColor(frame, cv2.COLOR_RGB2BGR),
            "Calibrated Board": warped_overlay,
            "Chess State":     board_image,
            "Info":            info_panel,
        }

    def _build_info_lines(self) -> list[str]:
        changed_names = ", ".join(f["name"] for f in self._changed_fields[:6])
        status = "KI-Zug nachziehen, dann 'n' drücken" if self._waiting_for_board_update else (
            "Weiß" if self._board.turn == chess.WHITE else "Schwarz"
        )
        return [
            "Taste 'n': neues Foto nach Zug",
            "Taste 's': Referenz neu setzen",
            "Taste 'q': Beenden",
            "",
            f"Letzter Zug: {self._last_move_text}",
            f"Geänderte Felder: {changed_names or '–'}",
            f"Anzahl Änderungen: {len(self._changed_fields)}",
            "",
            f"Status: {status}",
            f"Zugnummer: {self._board.fullmove_number}",
        ]


    def run(self) -> None:
        input("Startposition aufbauen und ENTER drücken...")
        self._capture_reference()

        while True:
            frame = self._cam.capture_frame(False)
            if frame is None:
                continue

            warped = self._calibration.warp(frame)
            self._windows.show(self._build_frames(frame, warped))
            key = self._windows.wait_key()

            if key == "q":
                break
            elif key == "n":
                self._handle_new_photo()
            elif key == "s":
                self._handle_reset()