from flask import Flask, render_template, redirect, url_for, request
from blackjack import BlackjackGame, BlackjackGamePVP

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

# Jeu contre le croupier
game = BlackjackGame(starting_balance=500)

# Jeu 2 joueurs
game_pvp = BlackjackGamePVP()


@app.route("/")
def index():
    error = request.args.get("error")
    return render_template(
        "index.html",
        balance=game.balance,
        error=error,
        player_name=game.player_name,
        dealer_name=game.dealer_name,
        p1_name=game_pvp.player1_name,
        p2_name=game_pvp.player2_name,
    )


# ---------- MODE VS CROUPIER ----------

@app.route("/start", methods=["POST"])
def start():
    # nom du joueur
    name = request.form.get("player_name", "").strip()
    if name:
        game.player_name = name

    # mise
    try:
        bet_str = request.form.get("bet", "0")
        bet = int(bet_str)
    except ValueError:
        return redirect(url_for("index", error="Mise invalide."))

    if not game.can_bet(bet):
        return redirect(url_for("index", error="Mise impossible (montant trop élevé ou nulle)."))

    game.start_new_game(bet)
    return redirect(url_for("game_page"))


@app.route("/game")
def game_page():
    return render_template(
        "game.html",
        player_hand=game.player_hand,
        dealer_hand=game.dealer_hand,
        player_score=game.player_hand.score(),
        dealer_score=game.dealer_hand.score() if game.finished else None,
        finished=game.finished,
        message=game.message,
        balance=game.balance,
        bet=game.bet,
        player_name=game.player_name,
        dealer_name=game.dealer_name,
        history=game.history,
        result=game.last_result,
    )


@app.route("/hit")
def hit():
    game.player_hit()
    if game.finished:
        game.dealer_turn()
        game.resolve_round()
    return redirect(url_for("game_page"))


@app.route("/stand")
def stand():
    game.player_stand()
    game.dealer_turn()
    game.resolve_round()
    return redirect(url_for("game_page"))


@app.route("/reset-balance")
def reset_balance():
    game.reset_balance()
    return redirect(url_for("index"))


# ---------- MODE 2 JOUEURS ----------

@app.route("/start-pvp", methods=["POST"])
def start_pvp():
    name1 = request.form.get("player1_name", "").strip() or "Joueur 1"
    name2 = request.form.get("player2_name", "").strip() or "Joueur 2"

    game_pvp.start_new_game(name1, name2)
    return redirect(url_for("game_pvp_page"))


@app.route("/game-pvp")
def game_pvp_page():
    return render_template(
        "game_pvp.html",
        player1_hand=game_pvp.player1_hand,
        player2_hand=game_pvp.player2_hand,
        player1_score=game_pvp.player1_hand.score(),
        player2_score=game_pvp.player2_hand.score(),
        player1_name=game_pvp.player1_name,
        player2_name=game_pvp.player2_name,
        current_turn=game_pvp.current_turn,
        finished=game_pvp.finished,
        message=game_pvp.message,
        history=game_pvp.history,
        result=game_pvp.last_result,
    )


@app.route("/hit-pvp")
def hit_pvp():
    game_pvp.hit()
    return redirect(url_for("game_pvp_page"))


@app.route("/stand-pvp")
def stand_pvp():
    game_pvp.stand()
    return redirect(url_for("game_pvp_page"))


if __name__ == "__main__":
    app.run(debug=False)