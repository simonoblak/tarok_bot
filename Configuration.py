class Configuration:
    config = {}

    @staticmethod
    def read_config(file_name):
        print("Reading configuration")
        lines = [line.rstrip('\n') for line in open(file_name)]
        for line in lines:
            if not line.startswith("#"):
                setting = line.split("=")
                if len(setting) == 2:
                    try:
                        Configuration.config[setting[0]] = int(setting[1])
                    except ValueError:
                        Configuration.config[setting[0]] = setting[1]

        print("Configuration obtained")

    def get_config(self):
        return self.config
