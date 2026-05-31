from abc import ABC, abstractmethod

class ChessPlatform(ABC):

    @abstractmethod
    def new_game(self, level: int, color: str) -> str:
        """Startet ein neues Spiel, gibt eine game_id zurück."""
        
    @abstractmethod
    def submit_move(self, move: str) -> bool:
        """Sendet deinen Zug (UCI-Format, z.B. 'e2e4'). Gibt True zurück wenn erfolgreich."""

    @abstractmethod
    def get_opponent_move(self) -> str:
        """Fragt den letzten Zug des Gegners ab. Gibt UCI-String zurück."""

    @abstractmethod
    def resign(self) -> None:
        """Aufgeben."""