import os
from dotenv import load_dotenv
load_dotenv()

from vision.camera import Camera
from ui.calibration_ui import CalibrationUI
from ui.window_manager import WindowManager
from game.game_session import GameSession
from platform.lichess import LichessAI


def main() -> None:
    cam = Camera()
    if not cam.start_cam(0, (1920, 1080), 30):
        print("Kamera konnte nicht geöffnet werden.")
        return

    windows = WindowManager()
    windows.setup()

    calibration = CalibrationUI(cam, windows).run()
    if calibration is None:
        cam.close_cam()
        windows.destroy()
        return

    #lichess_ai = LichessAI(os.getenv('LICHESS_API_KEY'))
    #lichess_ai.new_game(level="3", color="white", time_control=None)

    session = GameSession(cam, calibration, windows)
    session.run()

    cam.close_cam()
    windows.destroy()


if __name__ == "__main__":
    main()