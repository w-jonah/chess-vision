from .base import ChessPlatform
import time
import requests
import json

class LichessAI(ChessPlatform):
    def __init__(self, token: str) -> None:
        self._access_token = token
        self._game_id = None
        self._known_move_count: int = 0

    def new_game(self, level: str, color: str = "random", time_control: tuple[str] = ("300", "1"), 
                 fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") -> None:
        res = requests.post("https://lichess.org/api/challenge/ai",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {self._access_token}"
            },
            data={
                "level": level,
                "clock.limit": time_control[0] if time_control is not None else "",
                "clock.increment": time_control[1] if time_control is not None else "",
                "days": "1",
                "color": color,
                "variant": "standard",
                "fen": fen
            }
        )
        res.raise_for_status()
        game_id = res.json()['id']
        self._game_id = game_id
        print(f"Neue Partie({game_id}) erfolgreich gestartet")
    
    def submit_move(self, move: str) -> bool:
        res = requests.post(f"https://lichess.org/api/board/game/{self._game_id}/move/{move}",
            headers={
                "Authorization": f"Bearer {self._access_token}"
            },
            params={
                "offeringDraw": "false"
            }
        )
        res.raise_for_status()
        print(f"Zug: {move} erfolgreich ausgeführt")
        self._known_move_count += 1 
        return True
    
    def get_opponent_move(self) -> str:
        with requests.get(
            f"https://lichess.org/api/board/game/stream/{self._game_id}",
            headers={"Authorization": f"Bearer {self._access_token}"},
            stream=True
        ) as response:
            for line in response.iter_lines():
                if not line:
                    continue

                event = json.loads(line)

                if event["type"] == "gameFull":
                    state = event["state"]
                elif event["type"] == "gameState":
                    state = event
                else:
                    continue

                moves = state["moves"].split() if state["moves"] else []
                if len(moves) > self._known_move_count:
                    self._known_move_count = len(moves)
                    return moves[-1]

    def resign(self) -> None:
        res = requests.post(f"https://lichess.org/api/board/game/{self._game_id}/resign",
            headers={
            "Authorization": f"Bearer {self._access_token}"
            }
        )
        res.raise_for_status()
        print("Erfolgreich aufgegeben")

    def takeback(self) -> None:
        res = requests.post(f"https://lichess.org/api/board/game/{self._game_id}/takeback/yes",
            headers={
                "Authorization": f"Bearer {self._access_token}"
            }
        )
        res.raise_for_status()