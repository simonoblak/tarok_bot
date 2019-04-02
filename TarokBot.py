from karte import Deck

print("Start...")


def read_conf(file_name):
    print("Reading configuration")
    lines = [line.rstrip('\n') for line in open(file_name)]
    properties = {}
    for line in lines:
        setting = line.split("=")
        if len(setting) == 2:
            try:
                properties[setting[0]] = int(setting[1])
            except ValueError:
                properties[setting[0]] = setting[1]

    print("Configuration obtained")
    return properties


conf = read_conf("resources/configuration.txt")
# print(conf)

deck = Deck.Deck()

deck.shuffle_deck(conf["min_cut_shuffle"],
                  conf["max_cut_shuffle"],
                  conf["min_number_of_shuffles"],
                  conf["max_number_of_shuffles"])

print("----------CARD ORDER----------")
for kard in deck.deck:
    print(kard.get_card_name() + "-> Points: " + kard.points + "; Rank: " + kard.rank)
print("------------------------------")

# Shuffle cards
# Deal
# Bot logic

