import Configuration


print("Start...")

# Reading configuration.txt file
Configuration.Configuration().read_config("resources/documents/configuration.txt")
Configuration.Configuration().check_config()

import TarokBot

if __name__ == '__main__':
    TarokBot.tarok_bot()
