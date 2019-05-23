import Configuration
from players import Player
from karte import Deck


config = Configuration.Configuration().get_config()


class Table:
    def __init__(self):
        self.player_number = config["player_number"]
        self.number_of_cards = self.get_number_of_cards()
        self.players = []
        self.starting_player = int(config["starting_player"])
        self.deck = []
        self.talon = []
        self.on_table = []
        self.playing = []
        self.opposing = []
        self.game_indexes = []

    def get_number_of_cards(self):
        if self.player_number == 4:
            return 12
        elif self.player_number == 3:
            return 16
        return None

    def set_table(self):
        if "player_names" in config:
            player_names = config["player_names"].split(",")
        else:
            player_names = input("Insert names sepperated with a comma: ").split(",")
        # self.starting_player = player_names[0]

        for i in range(len(player_names)):
            self.players.append(Player.Player(player_names[i]))

    def deal_cards(self):
        does_everyone_have_a_tarok_card = True
        while True:
            card_start = 0
            card_end = self.number_of_cards
            self.deck = Deck.Deck().get_deck()
            """
            print("----------CARD ORDER----------")
            c = 0
            for kard in self.deck:
                print(str(c) + ". " + kard.get_card_name())
                c += 1
            print("------------------------------")
            """
            for i in range(self.player_number):
                self.players[i].cards = self.deck[card_start:card_end]
                card_end += self.number_of_cards
                card_start += self.number_of_cards
            self.talon = self.deck[-6:]

            for playa in self.players:
                if not playa.check_if_has_tarok_card():
                    does_everyone_have_a_tarok_card = False

            if does_everyone_have_a_tarok_card:
                break
            else:
                Deck.Deck().shuffle_deck(config["min_cut_shuffle"],
                                         config["max_cut_shuffle"],
                                         config["min_number_of_shuffles"],
                                         config["max_number_of_shuffles"])

    def split_talon(self, game_index):
        if game_index == 3:
            return [self.talon[:3], self.talon[3:]]
        if game_index == 2:
            return [self.talon[:2], self.talon[2:4], self.talon[4:]]
        if game_index == 1:
            return [self.talon[0], self.talon[1], self.talon[2], self.talon[3], self.talon[4], self.talon[5]]
        return []

    def is_obvezna_3(self):
        obvezna3 = config["obvezna3"]
        if obvezna3 == "True":
            return True
        elif obvezna3 == "False":
            return False
        return None

    # if priority True then that player can choose the game over another player, otherwise False
    def is_game_valid(self, index, best, priority):
        try:
            game = int(index)
            best_game = int(best)
            if 0 <= game <= best_game:
                if priority and game <= best_game or not priority and game < best_game:
                    return True
            return False

            # if not((priority and 0 <= game <= best_game) or (not priority and 0 <= game < best_game)):
        except ValueError:
            print("Invalid value or you don't play")
            return False

    def best_game_text(self, best_game):
        bgt = ""
        for i in range(best_game, -1, -1):
            bgt += str(i) + " "
        return "|, please insert game value (" + bgt + "): "

    def choose_game(self):
        print("choose_game(self): Choose who plays the game")
        best_game = 3
        game_text = self.best_game_text(best_game)
        # ideja je da podam 1. igralca na index 0 v player_games ker tako lahko lažje določam prednost
        player_games = self.players[self.starting_player:] + self.players[:self.starting_player]

        # choosing_player = self.starting_player

        index = 0
        best_player_index = 0
        while True:
            for i in player_games:
                print(i.name + ": " + str(i.play))
            game_value = input("\nHey |" + player_games[index].name + game_text)
            print("------------------------------------------------------------")

            if self.is_game_valid(game_value, best_game, index <= best_player_index):
                player_games[index].play = int(game_value)
                best_game = int(game_value)
                best_player_index = index
                index += 1
            else:
                del player_games[index]
                if index < best_player_index:
                    best_player_index -= 1

            if len(player_games) < 2:
                break
            elif index >= len(player_games):
                index = 0

        print(player_games[0].name + " will play in " + str(player_games[0].play))
