from ProjectConstants.TerminalColors import TerminalColors
from datetime import datetime
import Configuration


class Logs:
    log_settings = []

    @staticmethod
    def init_logs():
        try:
            Logs.log_settings = Configuration.Configuration().get_config()["log_level"].split(",")
        except KeyError:
            print(TerminalColors.FAIL + "First startup" + TerminalColors.ENDC)

    @staticmethod
    def error_message(message):
        if "error" in Logs.log_settings:
            Logs.print_message(message, LogLevels.ERROR, TerminalColors.FAIL)

    @staticmethod
    def warning_message(message):
        if "warning" in Logs.log_settings:
            Logs.print_message(message, LogLevels.WARNING, TerminalColors.WARNING)

    @staticmethod
    def info_message(message):
        if "info" in Logs.log_settings:
            Logs.print_message(message, LogLevels.INFO, TerminalColors.OKBLUE)

    @staticmethod
    def debug_message(message):
        if "debug" in Logs.log_settings:
            Logs.print_message(message, LogLevels.DEBUG)

    @staticmethod
    def print_message(message, level, terminal_color=None):
        if isinstance(message, str):
            if terminal_color is None:
                print(Logs.get_timestamp() + level + message)
            else:
                print(Logs.get_timestamp() + terminal_color + level + message + TerminalColors.ENDC)
            return
        try:
            if terminal_color is None:
                print(Logs.get_timestamp() + level + str(message))
            else:
                print(Logs.get_timestamp() + terminal_color + level + str(message) + TerminalColors.ENDC)
        except TypeError:
            print(
                Logs.get_timestamp() + TerminalColors.UNDERLINE + "Could not print input message" + TerminalColors.ENDC
            )

    @staticmethod
    def get_timestamp(date_sep="-", time_sep=":"):
        ts = datetime.now()
        return f"{ts.year:04d}" + date_sep + \
            f"{ts.month:02d}" + date_sep + \
            f"{ts.day:02d}" + " " + \
            f"{ts.hour:02d}" + time_sep + \
            f"{ts.minute:02d}" + time_sep + \
            f"{ts.second:02d}" + time_sep + \
            f"{ts.microsecond}" + " "


class LogLevels:
    DEBUG = "<DEBUG>: "
    INFO = "<INFO>: "
    WARNING = "<WARNING>: "
    ERROR = "<ERROR>: "
