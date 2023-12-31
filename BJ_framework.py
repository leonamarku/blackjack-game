import tkinter as tk
from tkinter import PhotoImage, messagebox
import random

class Card:
    def __init__(self, suit: str, value: str):
        self.suit = suit
        self.value = value

    def get_numeric_value(self) -> int:
        if self.value in ['K', 'Q', 'J']:
            return 10
        elif self.value == 'A':
            return 11
        else:
            return int(self.value)

    def get_image(self):
        return f"img/{self.value}_of_{self.suit}.png"

class Deck:
    def __init__(self, suits=None, values=None):
        # Use default values for suits and values if not provided
        self.cards = [Card(suit, value) for value in values or ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
                                         for suit in suits or ['hearts', 'diamonds', 'clubs', 'spades']]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self) -> Card:
        if not self.cards:
            raise ValueError("Deck is empty")
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card: Card):
        self.cards.append(card)

    def value(self) -> int:
        total_value = sum(card.get_numeric_value() for card in self.cards)
        num_aces = sum(1 for card in self.cards if card.value == 'A')

        while total_value > 21 and num_aces:
            total_value -= 10
            num_aces -= 1

        return total_value

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = Hand()

class BlackjackGame:
    def __init__(self):
        self.player = Player("Player")
        self.dealer = Player("Dealer")
        self.deck = Deck()
        self.deck.shuffle()

    def start_game(self):
        self.player.hand = Hand()
        self.dealer.hand = Hand()

        for _ in range(2):
            self.player.hand.add_card(self.deck.deal())
            self.dealer.hand.add_card(self.deck.deal())

    def hit(self) -> bool:
        self.player.hand.add_card(self.deck.deal())
        return self.player.hand.value() > 21

    def dealer_hit(self) -> bool:
        if self.dealer.hand.value() >= 17:
            return False
        self.dealer.hand.add_card(self.deck.deal())
        return self.dealer.hand.value() <= 21

    def determine_winner(self):
        player_value = self.player.hand.value()
        dealer_value = self.dealer.hand.value()

        if player_value > 21:
            return "You've busted! The house wins."

        if dealer_value > 21:
            return "Dealer busts! You win."

        if player_value > dealer_value:
            return "You win!"
        elif dealer_value > player_value:
            return "Dealer wins."
        else:
            return "It's a tie!"

class BlackjackGUI:
    def __init__(self, game):
        self.game = game

        self.root = tk.Tk()
        self.root.title("Blackjack")

        self.create_frames()
        self.create_stand_button()
        self.start_game()

    def create_frames(self):
        # Frames for the player and the dealer
        self.player_frame = tk.Frame(self.root)
        self.player_frame.pack(side=tk.LEFT, padx=10)

        self.deck_frame = tk.Frame(self.root)
        self.deck_frame.pack(side=tk.LEFT, padx=10)

        self.dealer_frame = tk.Frame(self.root)
        self.dealer_frame.pack(side=tk.RIGHT, padx=10)

    def create_stand_button(self):
        # "Stand" button
        self.btn_stand = tk.Button(self.deck_frame, text="Stand", command=self.handle_stand, state=tk.NORMAL)
        self.btn_stand.pack(side=tk.BOTTOM)

    def start_game(self):
        self.game.start_game()
        self.update_interface()

    def handle_hit(self, event):
        try:
            if self.game.hit():
                self.update_interface()
                self.end_game("You've busted! The house wins.")
                return
            self.update_interface()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def handle_stand(self):
        self.btn_stand.config(state=tk.DISABLED)
        self.process_dealer_hit()

    def process_dealer_hit(self):
        try:
            if self.game.dealer_hit():
                self.update_interface()
                self.root.after(1000, self.process_dealer_hit)
            else:
                self.end_game(self.game.determine_winner())
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def update_interface(self):
        # Remove all widgets from player, deck, and dealer frames
        for frame in [self.player_frame, self.deck_frame, self.dealer_frame]:
            for widget in frame.winfo_children():
                widget.destroy()

        # Player's cards
        player_previous_frame = tk.Frame(self.player_frame)
        player_previous_frame.pack(side=tk.LEFT, pady=10)

        for card in self.game.player.hand.cards[:-1]:
            img = self.get_resized_image(card)
            lbl = tk.Label(player_previous_frame, image=img)
            lbl.image = img
            lbl.pack(side=tk.TOP, pady=5)

        # The last card of the player in the center
        last_card = self.game.player.hand.cards[-1]
        img = self.get_resized_image(last_card)
        lbl = tk.Label(self.player_frame, image=img)
        lbl.image = img
        lbl.pack(side=tk.LEFT, padx=10)

        # Deck in the middle
        img = PhotoImage(file="img/card_back_01.png")
        lbl = tk.Label(self.deck_frame, image=img, cursor="hand2")
        lbl.image = img
        lbl.pack(side=tk.TOP, padx=10)
        lbl.bind("<Button-1>", self.handle_hit)

        # "Stand" button below the deck
        self.btn_stand = tk.Button(self.deck_frame, text="Stand", command=self.handle_stand, state=tk.NORMAL)
        self.btn_stand.pack(side=tk.BOTTOM)

        # Dealer's cards
        dealer_previous_frame = tk.Frame(self.dealer_frame)
        dealer_previous_frame.pack(side=tk.RIGHT, pady=10)

        for card in self.game.dealer.hand.cards[:-1]:
            img = self.get_resized_image(card)
            lbl = tk.Label(dealer_previous_frame, image=img)
            lbl.image = img
            lbl.pack(side=tk.TOP, pady=5)

        # The last card of the dealer in the center
        last_card = self.game.dealer.hand.cards[-1]
        img = self.get_resized_image(last_card)
        lbl = tk.Label(self.dealer_frame, image=img)
        lbl.image = img
        lbl.pack(side=tk.RIGHT, padx=10)

    def get_resized_image(self, card):
        img = PhotoImage(file=card.get_image())
        return img.subsample(3, 3)

    def end_game(self, message):
        messagebox.showinfo("Result", message)
        self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game_logic = BlackjackGame()
    app = BlackjackGUI(game_logic)
    app.run()
