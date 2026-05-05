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

def evaluate_board(board):
    """Simple material evaluation."""
    score = 0
    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type]
        score += value if piece.color == chess.WHITE else -value
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

    def to_dict(self):
        return {
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn else "black",
            "pending_qte": bool(self.pending_qte),
            "mode": self.mode,
            "ai_side": self.ai_side,
        }

    def try_move(self, move_uci):
        move = chess.Move.from_uci(move_uci)

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
            self.board.remove_piece_at(move.from_square)
            winner = defender

        self.pending_qte = None
        return winner
