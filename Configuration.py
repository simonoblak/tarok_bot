class Configuration:
    config = {}

    @staticmethod
    def read_config(file_name):
        print("Reading configuration")
        lines = [line.rstrip('\n') for line in open(file_name, 'r', encoding='utf8')]
        for line in lines:
            if not line.startswith("#"):
                setting = line.split("=")
                if len(setting) == 2:
                    # Note, isdigit() does not work for float or negative numbers
                    Configuration.config[setting[0]] = int(setting[1]) if setting[1].isdigit() else setting[1]

        print("Configuration obtained")

    def get_config(self):
        return self.config

    def pretty_print(self, not_pretty_text, line_length=64):
        line_half_length = int((line_length - len(not_pretty_text)) / 2)
        lines = "-" * line_half_length
        print(lines + not_pretty_text.upper() + lines)

    def check_config(self):
        errors = []
        if not 3 <= self.config["player_number"] <= 4:
            errors.append("player_number number must be 3 or 4")

        if not self.config["url"].startswith("http"):
            errors.append("url should start with http")

        if not self.config["opponent_bot"] == "Vražji" \
                and not self.config["opponent_bot"] == "Težek":
            errors.append("opponent_bot can only be 'Vražji' or 'Težek'")

        if not self.config["playing_bot"] == "RandomBot" \
                and not self.config["playing_bot"] == "SemiBot" \
                and not self.config["playing_bot"] == "WonderfulBot":
            errors.append("playing_bot can only be 'RandomBot' or 'SemiBot' or 'WonderfulBot'")

        not_allowed_games = ["Valat", "Barvni valat", "Odprti berač", "Berač",
                             "Solo tri", "Solo dve", "Solo ena", "Solo brez"]
        for game in self.config["not_allowed_games"].split(","):
            if game not in not_allowed_games:
                errors.append("Not allowed games parameter has an unexpected value")

        if not self.config["is_pass_encoded"] == "yes" and not self.config["is_pass_encoded"] == "no":
            errors.append("'is_pass_encoded' can only have 'yes' or 'no' values")

        if not 0 < self.config["min_important_tarot"] < 23:
            errors.append("'min_important_tarot' must be between 1 and 22")

        allowed_log_settings = ["debug", "info", "warning", "error"]
        log_settings = self.config["log_level"].split(",")
        for setting in log_settings:
            if setting not in allowed_log_settings:
                errors.append("'" + setting + "' is not allowed in log_level")

        if self.config["write_to_database"] != "yes" and self.config["write_to_database"] != "no":
            errors.append("'write_to_database' can only have 'yes' or 'no' values")

        if self.config["start_admin"] != "yes" and self.config["start_admin"] != "no":
            errors.append("'start_admin' can only have 'yes' or 'no' values")

        if len(errors) > 0:
            self.pretty_print("fix these errors")
            for e in errors:
                print(e)
            raise ValueError("Some of the configuration values are NOT ok!!!")