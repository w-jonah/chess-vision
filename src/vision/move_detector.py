from typing import List
import chess

class MoveDetector:
    @staticmethod
    def get_affected_squares(board: chess.Board, move: chess.Move) -> set[str]:
        affected = set()
        
        if board.is_castling(move):
            # Rochaden: König und Turm bewegng
            king_from = chess.square_name(move.from_square)
            king_to = chess.square_name(move.to_square)
            affected.add(king_from)
            affected.add(king_to)
            
            # Kurze Rochade
            if move.to_square in [chess.G1, chess.G8]:
                rook_from = "h1" if move.from_square == chess.E1 else "h8"
                rook_to = "f1" if move.from_square == chess.E1 else "f8"
            # Lange Rochade
            else:  
                rook_from = "a1" if move.from_square == chess.E1 else "a8"
                rook_to = "d1" if move.from_square == chess.E1 else "d8"
            
            affected.add(rook_from)
            affected.add(rook_to)
        else:
            # Normaler Zug
            from_sq = chess.square_name(move.from_square)
            to_sq = chess.square_name(move.to_square)
            affected.add(from_sq)
            affected.add(to_sq)
            
            # En Passant
            if board.is_en_passant(move):
                captured_square = move.to_square - 8 if board.turn else move.to_square + 8
                affected.add(chess.square_name(captured_square))

        return affected

    @staticmethod
    def detect_move(board: chess.Board, changed_squares: List[str]) -> str | None:
        if not changed_squares:
            return None

        changed_set = set(changed_squares)
        perfect_candidates: list[chess.Move] = []
        partial_candidates: list[chess.Move] = []

        for move in board.legal_moves:
            affected_squares = MoveDetector.get_affected_squares(board, move)

            if affected_squares == changed_set:
                perfect_candidates.append(move)

            elif affected_squares <= changed_set:
                partial_candidates.append(move)

        # Perfekte Übereinstimmung
        if len(perfect_candidates) == 1:
            return perfect_candidates[0].uci()
        if perfect_candidates:
            return perfect_candidates[0].uci()

        # Teilweise Überwinstimmung
        if len(partial_candidates) == 1:
            return partial_candidates[0].uci()

        #Fallback
        return partial_candidates[0].uci() if partial_candidates else None
