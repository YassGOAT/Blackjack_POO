import random

# Liste de noms possibles pour le bot (One Piece + Dragon Ball Super)
BOT_NAMES = [
    "Zoro",
    "Nami",
    "Sanji",
    "Robin",
    "Law",
    "Beerus",
    "Whis",
    "Hit",
    "Jiren",
    "Kale",
]


class Card:
    def __init__(self, value, suit):
        self.value = value      # "A", "2", ..., "K"
        self.suit = suit        # "Pique", "Trèfle", "Carreau", "Cœur"

    def __str__(self):
        return f"{self.value} de {self.suit}"


class Deck:
    def __init__(self):
        values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        suits = ["Pique", "Trèfle", "Carreau", "Cœur"]
        self.cards = [Card(v, s) for s in suits for v in values]
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            self.__init__()  # recrée un paquet si vide
        return self.cards.pop()


class Hand:
    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def score(self):
        total = 0
        aces = 0
        for c in self.cards:
            if c.value in ["J", "Q", "K"]:
                total += 10
            elif c.value == "A":
                total += 11
                aces += 1
            else:
                total += int(c.value)

        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    def is_bust(self):
        return self.score() > 21


class BlackjackGame:
    def __init__(self, starting_balance=500):
        self.starting_balance = starting_balance
        self.balance = starting_balance
        self.bet = 0
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.finished = False
        self.message = ""

        # Noms
        self.dealer_names = BOT_NAMES
        self.player_name = "Joueur"
        self.dealer_name = random.choice(self.dealer_names)

        # Historique des parties
        self.history = []

        # NEW : dernier résultat brut ("Victoire", "Défaite", "Égalité" ou "")
        self.last_result = ""

    def reset_balance(self):
        self.balance = self.starting_balance
        self.bet = 0
        self.message = "Solde réinitialisé."
        # si tu veux aussi vider l'historique :
        # self.history = []

    def can_bet(self, amount: int) -> bool:
        return 0 < amount <= self.balance

    def start_new_game(self, bet: int):
        """Démarre une manche avec une mise donnée."""
        if not self.can_bet(bet):
            raise ValueError("Mise invalide")

        self.bet = bet
        self.balance -= bet

        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.finished = False
        self.message = ""

        # nouveau nom aléatoire pour le bot à chaque manche
        self.dealer_name = random.choice(self.dealer_names)

        if len(self.deck.cards) < 15:
            self.deck = Deck()

        # distribution initiale
        self.player_hand.add(self.deck.draw())
        self.player_hand.add(self.deck.draw())
        self.dealer_hand.add(self.deck.draw())
        self.dealer_hand.add(self.deck.draw())

    def player_hit(self):
        if self.finished:
            return
        self.player_hand.add(self.deck.draw())
        if self.player_hand.is_bust():
            self.finished = True

    def player_stand(self):
        if self.finished:
            return
        self.finished = True

    def dealer_turn(self):
        if self.player_hand.is_bust():
            return

        while self.dealer_hand.score() < 17:
            self.dealer_hand.add(self.deck.draw())

    def resolve_round(self):
        """Calcule le résultat final, met à jour le solde et log dans l'historique."""
        ps = self.player_hand.score()
        ds = self.dealer_hand.score()
        result = ""

        if ps > 21:
            self.message = f"Tu as dépassé 21 ({ps}). Tu perds {self.bet} €."
            result = "Défaite"
        elif ds > 21:
            gain = self.bet * 2
            self.balance += gain
            self.message = (
                f"{self.dealer_name} dépasse 21 ({ds}). Tu gagnes {gain} € !"
            )
            result = "Victoire"
        elif ps > ds:
            gain = self.bet * 2
            self.balance += gain
            self.message = (
                f"Tu bats {self.dealer_name} ! "
                f"(Toi : {ps} / {self.dealer_name} : {ds}) Tu gagnes {gain} €."
            )
            result = "Victoire"
        elif ps < ds:
            self.message = (
                f"{self.dealer_name} gagne. "
                f"(Toi : {ps} / {self.dealer_name} : {ds}) Tu perds {self.bet} €."
            )
            result = "Défaite"
        else:
            self.balance += self.bet
            self.message = (
                f"Égalité ({ps}). Ta mise de {self.bet} € t'est rendue."
            )
            result = "Égalité"

        self.last_result = result

        # --- Ajout dans l'historique ---
        entry = {
            "result": result,
            "player_score": ps,
            "dealer_score": ds,
            "bet": self.bet,
            "balance_after": self.balance,
            "dealer_name": self.dealer_name,
        }
        # on ajoute en tête de liste
        self.history.insert(0, entry)
        # on limite à 10 entrées
        if len(self.history) > 10:
            self.history.pop()

class BlackjackGamePVP:
    """Mode 2 joueurs sur le même écran (sans croupier)."""

    def __init__(self):
        self.deck = Deck()
        self.player1_hand = Hand()
        self.player2_hand = Hand()

        self.player1_name = "Joueur 1"
        self.player2_name = "Joueur 2"

        self.current_turn = "p1"  # "p1" ou "p2"
        self.finished = False
        self.message = ""
        self.last_result = ""  # "Victoire", "Défaite", "Égalité" (du point de vue du Joueur 1)

        # Historique des parties
        self.history = []

    def _reset_hands(self):
        self.player1_hand = Hand()
        self.player2_hand = Hand()

    def start_new_game(self, name1: str, name2: str):
        """Démarre une nouvelle manche PVP."""
        if name1:
            self.player1_name = name1
        if name2:
            self.player2_name = name2

        # On recrée le deck si presque vide
        if len(self.deck.cards) < 15:
            self.deck = Deck()

        self._reset_hands()
        self.finished = False
        self.message = ""
        self.last_result = ""
        self.current_turn = "p1"

        # 2 cartes pour chaque joueur
        self.player1_hand.add(self.deck.draw())
        self.player1_hand.add(self.deck.draw())
        self.player2_hand.add(self.deck.draw())
        self.player2_hand.add(self.deck.draw())

    def hit(self):
        """Le joueur courant tire une carte."""
        if self.finished:
            return

        hand = self.player1_hand if self.current_turn == "p1" else self.player2_hand
        hand.add(self.deck.draw())

        if hand.is_bust():
            # s'il bust, on passe au suivant ou on termine
            if self.current_turn == "p1":
                self.current_turn = "p2"
            else:
                self.finished = True
                self._resolve_round()

    def stand(self):
        """Le joueur courant reste."""
        if self.finished:
            return

        if self.current_turn == "p1":
            self.current_turn = "p2"
        else:
            self.finished = True
            self._resolve_round()

    def _resolve_round(self):
        """Compare les deux joueurs et enregistre le résultat."""
        s1 = self.player1_hand.score()
        s2 = self.player2_hand.score()

        result = ""
        winner_name = None

        p1_bust = s1 > 21
        p2_bust = s2 > 21

        if p1_bust and p2_bust:
            result = "Égalité"
            self.message = (
                f"Les deux joueurs dépassent 21 ({s1} / {s2}). Personne ne gagne."
            )
        elif p1_bust and not p2_bust:
            result = "Défaite"  # du point de vue du Joueur 1
            winner_name = self.player2_name
            self.message = (
                f"{self.player1_name} dépasse 21 ({s1}). "
                f"{self.player2_name} gagne avec {s2}."
            )
        elif p2_bust and not p1_bust:
            result = "Victoire"
            winner_name = self.player1_name
            self.message = (
                f"{self.player2_name} dépasse 21 ({s2}). "
                f"{self.player1_name} gagne avec {s1}."
            )
        else:
            # aucun ne bust, on compare les scores
            if s1 > s2:
                result = "Victoire"
                winner_name = self.player1_name
                self.message = (
                    f"{self.player1_name} gagne ! "
                    f"({self.player1_name} : {s1} / {self.player2_name} : {s2})"
                )
            elif s2 > s1:
                result = "Défaite"
                winner_name = self.player2_name
                self.message = (
                    f"{self.player2_name} gagne ! "
                    f"({self.player1_name} : {s1} / {self.player2_name} : {s2})"
                )
            else:
                result = "Égalité"
                self.message = (
                    f"Égalité parfaite ({s1} / {s2}). "
                    f"Aucun des deux ne l'emporte."
                )

        self.last_result = result

        entry = {
            "result": result,
            "p1_score": s1,
            "p2_score": s2,
            "p1_name": self.player1_name,
            "p2_name": self.player2_name,
            "winner_name": winner_name,
        }
        self.history.insert(0, entry)
        if len(self.history) > 10:
            self.history.pop()
