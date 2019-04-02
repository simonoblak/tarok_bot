from karte import Deck

print("Start...")


def read_conf(file_name):
    print("Reading configuration")
    lines = [line.rstrip('\n') for line in open(file_name)]
    properties = {}
    for line in lines:
        setting = line.split("=")
        if len(setting) != 2:
            print("CONFIGURATION SETTING not properly written")
        else:
            properties[setting[0]] = setting[1]
    print("Configuration obtained")
    return properties


conf = read_conf("resources/configuration.txt")
print(conf)


deck = Deck.Deck()

for kard in deck.deck:
    print(kard.get_card_name())



