import chess
import random
import math


DIRECTIONS = ["Up", "Down", "Left", "Right"]

def generate_qte_sequence(length=8):
    return [random.choice(DIRECTIONS) for _ in range(length)]

def compute_player_score(events):
    score = 0
    for e in events:
        if not e["hit"]:
            continue
        if e["timing_error"] < 0.05:
            score += 100
        elif e["timing_error"] < 0.15:
            score += 70
        else:
            score += 40
    return score

def ai_qte_score(difficulty="medium"):
    if difficulty == "easy":
        return random.randint(20, 60)
    if difficulty == "medium":
        return random.randint(40, 80)
    if difficulty == "hard":
        return random.randint(70, 100)

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}

# Piece-square tables (from white's perspective, row 0 is rank 8, row 7 is rank 1)
PAWN_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]

BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]

ROOK_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, 0, 0, 5, 5, 0, 0, 0]
]

QUEEN_TABLE = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]

KING_TABLE = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20]
]

PIECE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}

def evaluate_board(board):
    """Material and positional evaluation."""
    score = 0
    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type]
        row, col = divmod(square, 8)
        table = PIECE_TABLES[piece.piece_type]
        if piece.color == chess.WHITE:
            pos_value = table[row][col]
        else:
            pos_value = table[7 - row][col]  # Mirror for black
        total_value = value + pos_value
        score += total_value if piece.color == chess.WHITE else -total_value
    
    # King safety and attack bonus.
    white_king_sq = board.king(chess.WHITE)
    black_king_sq = board.king(chess.BLACK)

    if white_king_sq is not None:
        white_king_attackers = len(board.attackers(chess.BLACK, white_king_sq))
        score -= white_king_attackers * 20

    if black_king_sq is not None:
        black_king_attackers = len(board.attackers(chess.WHITE, black_king_sq))
        score += black_king_attackers * 20

    if board.is_check():
        score += 120 if board.turn == chess.WHITE else -120

    # Mobility bonus
    mobility = len(list(board.legal_moves))
    score += mobility * 5 if board.turn == chess.WHITE else -mobility * 5
    
    return score

def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)

    if maximizing:
        max_eval = -math.inf
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval

    else:
        min_eval = math.inf
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def choose_ai_move(board, depth=2):
    """Returns the best move using minimax."""
    best_move = None
    best_value = -math.inf if board.turn else math.inf

    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, -math.inf, math.inf, not board.turn)
        board.pop()

        if board.turn:  # white to move
            if value > best_value:
                best_value = value
                best_move = move
        else:  # black to move
            if value < best_value:
                best_value = value
                best_move = move

    return best_move

class Game:
    def __init__(self, mode="pvc", ai_side="black", difficulty="medium"):
        self.board = chess.Board()
        self.mode = mode
        self.ai_side = ai_side
        self.difficulty = difficulty
        self.pending_qte = None

    def _king_status(self):
        return self.board.king(chess.WHITE), self.board.king(chess.BLACK)

    def get_game_status(self):
        white_king, black_king = self._king_status()
        if white_king is None or black_king is None:
            winner = "white" if black_king is None else "black" if white_king is None else None
            return {
                "finished": True,
                "result": "win" if winner else "draw",
                "winner": winner,
                "reason": "king_capture",
            }

        if self.board.is_game_over():
            outcome = self.board.outcome()
            if outcome is not None:
                reason = outcome.termination.name.lower().replace("_", " ")
                if outcome.winner is not None:
                    return {
                        "finished": True,
                        "result": "win",
                        "winner": "white" if outcome.winner else "black",
                        "reason": reason,
                    }
                return {
                    "finished": True,
                    "result": "draw",
                    "winner": None,
                    "reason": reason,
                }
            return {
                "finished": True,
                "result": "draw",
                "winner": None,
                "reason": "game over",
            }

        return {"finished": False}

    def to_dict(self):
        return {
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn else "black",
            "pending_qte": bool(self.pending_qte),
            "mode": self.mode,
            "ai_side": self.ai_side,
            "game_status": self.get_game_status(),
        }

    def try_move(self, move_uci):
        move = chess.Move.from_uci(move_uci)

        if self.get_game_status()["finished"]:
            return {"type": "finished", "status": self.get_game_status()}

        if move not in self.board.legal_moves:
            return {"type": "illegal"}

        if self.board.is_capture(move):
            attacker_color = "white" if self.board.turn else "black"
            attacker_piece = self.board.piece_at(move.from_square)
            defender_piece = self.board.piece_at(move.to_square)

            sequence = generate_qte_sequence()

            self.pending_qte = {
                "move": move,
                "attacker_color": attacker_color,
                "attacker": attacker_piece.symbol(),
                "defender": defender_piece.symbol(),
                "sequence": sequence,
            }

            return {
                "type": "qte",
                "attacker": attacker_piece.symbol(),
                "defender": defender_piece.symbol(),
                "sequence": sequence,
            }

        # Normal move
        self.board.push(move)
        return {"type": "normal"}

    def resolve_qte(self, scores):
        q = self.pending_qte
        attacker = q["attacker_color"]
        defender = "white" if attacker == "black" else "black"

        attacker_score = scores[attacker]
        defender_score = scores[defender]

        move = q["move"]

        if attacker_score >= defender_score:
            self.board.push(move)
            winner = attacker
        else:
            defender_piece = self.board.piece_at(move.to_square)
            if defender_piece is not None:
                self.board.remove_piece_at(move.to_square)
                self.board.remove_piece_at(move.from_square)
                self.board.set_piece_at(move.from_square, defender_piece)
            winner = defender

        self.pending_qte = None
        return winner
