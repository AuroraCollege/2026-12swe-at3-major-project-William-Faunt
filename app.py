from flask import Flask, request, jsonify
from chess_logic import Game, choose_ai_move, ai_qte_score

app = Flask(__name__)
games = {}

@app.post("/api/new_game")
def new_game():
    data = request.get_json()
    mode = data.get("mode", "pvc")
    ai_side = data.get("ai_side", "black")
    difficulty = data.get("difficulty", "medium")

    game_id = str(len(games) + 1)
    games[game_id] = Game(mode=mode, ai_side=ai_side, difficulty=difficulty)

    return jsonify({"game_id": game_id})

@app.get("/api/state/<gid>")
def get_state(gid):
    return jsonify(games[gid].to_dict())

@app.post("/api/move/<gid>")
def move(gid):
    game = games[gid]
    move_uci = request.json["move"]
    result = game.try_move(move_uci)

    if result["type"] == "qte":
        return jsonify(result)

    return jsonify({"state": game.to_dict()})

@app.post("/api/qte/<gid>")
def qte(gid):
    game = games[gid]
    scores = request.json["scores"]
    winner = game.resolve_qte(scores)
    return jsonify({"winner": winner, "state": game.to_dict()})

@app.post("/api/ai_move/<gid>")
def ai_move(gid):
    game = games[gid]
    move = choose_ai_move(game.board)
    result = game.try_move(move.uci())

    if result["type"] == "qte":
        return jsonify(result)

    return jsonify({"state": game.to_dict()})

if __name__ == "__main__":
    app.run(debug=True)
