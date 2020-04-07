import tkinter as tk
import tkinter.ttk as tkk
from Logs import Logs
from Configuration import Configuration
from DatabaseComponent.db import Db
import threading

config = Configuration().get_config()


class Admin(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
        self.bot_state = "set"
        self.last_row_id_from_db = None
        self.is_my_bot_playing = False

    def callback(self):
        self.window.quit()

    def set_bot_state(self, state):
        Logs.info_message("Admin.set_bot_state(): Setting state to -> " + state)
        self.bot_state = state

    def set_to_reset(self):
        self.set_bot_state("reset")

    def set_to_set(self):
        self.set_bot_state("set")

    # def set_my_bot_playing(self, state):
    #     Logs.info_message("Admin.set_my_bot_playing(): Setting to -> " + state.__str__())
    #     self.is_my_bot_playing = state
    #
    # def set_my_bot_true(self):
    #     self.set_my_bot_playing(True)
    #
    # def set_my_bot_false(self):
    #     self.set_my_bot_playing(False)

    def set_ID_to_corrupted(self, c_id=None):
        """
        If c_id is None then last row ID will be used.
        :param c_id:
        :return:
        """
        message = "Admin.set_ID_to_corrupted(): "
        if c_id is None:
            if self.last_row_id_from_db is None:
                self.info_label.configure(text="Corrupted ID is not possible", foreground=self.default_error_color)
                return
            c_id = str(self.last_row_id_from_db)
        elif not isinstance(c_id, str):
            Logs.warning_message(message + "corrupted ID is not string")
            self.info_label.configure(text="corrupted ID is not string", foreground=self.default_error_color)
            return
        Logs.debug_message(message + "ID to change is -> " + c_id)
        Db.connect_to_db()
        Db.execute_sql("UPDATE rounds SET is_corrupt=1 WHERE round_id=" + c_id + ";")
        Db.close_db()

    def set_specific_ID_to_corrupted(self):
        corrupted_round = self.input_id.get()
        if corrupted_round == "":
            self.info_label.configure(text="Input is blank", foreground=self.default_error_color)
            return

        corrupted_round.strip()
        if not corrupted_round.isdigit() and int(corrupted_round) <= 0:
            self.info_label.configure(text="Input must be a positive int", foreground=self.default_error_color)
            return
        self.set_ID_to_corrupted(corrupted_round)

    def run(self):
        message = "Admin.run(): "
        self.light_blue = "#add8e6"

        self.window_width = "400"
        self.window_height = "320"

        self.default_error_color = "red"
        self.default_color = "black"
        self.default_width = 10

        self.window = tk.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.callback())
        self.window.title("Admin Tool for bot")
        self.window.geometry(self.window_width + "x" + self.window_height)
        self.window.configure(background=self.light_blue)

        self.settings_frame = tk.Frame(self.window, highlightbackground="black", highlightcolor="black", highlightthickness=1, bg=self.light_blue)
        self.settings_frame.pack()

        self.info_label = tk.Label(self.window, text="", background=self.light_blue)
        self.info_label.place(relx=0.0, rely=1.0, anchor='sw')

        # ---------------------------------------------------------------------------------------------
        # ----------------------------------SET OR RESET FUNCTIONS-------------------------------------
        # ---------------------------------------------------------------------------------------------

        self.bot_difficulty_frame = tk.Frame(self.settings_frame, bg=self.light_blue)
        self.bot_difficulty_frame.pack()

        self.bot_difficulty_label = tk.Label(self.bot_difficulty_frame, text="Bot difficulty", anchor='w', bg=self.light_blue)
        self.bot_difficulty_label.pack(side=tk.LEFT)

        self.bot_difficulty_combobox = tkk.Combobox(self.bot_difficulty_frame, state='readonly', width=self.default_width)
        all_bots = config["all_bots"].split(",")
        self.bot_difficulty_combobox['values'] = all_bots
        self.bot_difficulty_combobox.current(all_bots.index(config["playing_bot"]))  # set the selected item
        self.bot_difficulty_combobox.pack(side=tk.RIGHT)

        self.functions_frame = tk.Frame(self.settings_frame, bg=self.light_blue)
        self.functions_frame.pack()

        self.continue_button = tk.Button(self.functions_frame, text="Continue", command=self.set_to_set)
        self.continue_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.functions_frame, text="Stop", command=self.set_to_reset)
        self.stop_button.pack(side=tk.RIGHT)


        # self.my_bot_playing = tk.Frame(self.settings_frame, bg=self.light_blue)
        # self.functions_frame.pack()
        #
        # self.my_bot_playing_label = tk.Label(self.my_bot_playing, text="Is my bot playing: ", anchor='w', bg=self.light_blue)
        # self.my_bot_playing_label.pack(side=tk.LEFT)
        #
        # self.my_bot_playing_true_button = tk.Button(self.functions_frame, text="Yes", command=self.set_my_bot_true)
        # self.continue_button.pack(side=tk.LEFT)
        #
        # self.my_bot_playing_false_button = tk.Button(self.functions_frame, text="No", command=self.set_my_bot_false)
        # self.stop_button.pack(side=tk.RIGHT)

        # ---------------------------------------------------------------------------------------------
        # ------------------------------------SET ID TO CORRUPTED--------------------------------------
        # ---------------------------------------------------------------------------------------------

        self.corr_frame = tk.Frame(self.settings_frame, bg=self.light_blue)
        self.corr_frame.pack()

        self.corr_label = tk.Label(self.corr_frame, text="ID to set corrupted", bg=self.light_blue)
        self.corr_label.pack(side=tk.LEFT)

        self.input_id = tk.Entry(self.corr_frame, width=self.default_width)
        self.input_id.pack(side=tk.RIGHT)

        self.set_corr_frame = tk.Frame(self.settings_frame, bg=self.light_blue)
        self.set_corr_frame.pack()

        self.corr_id = tk.Button(self.set_corr_frame, text="Set Corrupted ID", command=self.set_specific_ID_to_corrupted)
        self.corr_id.pack(side=tk.LEFT)

        self.set_last_corr_frame = tk.Frame(self.settings_frame, bg=self.light_blue)
        self.set_last_corr_frame.pack()

        self.last_corr_id = tk.Button(self.set_last_corr_frame, text="Set Last ID Corrupted", command=self.set_ID_to_corrupted)
        self.last_corr_id.pack(side=tk.LEFT)
        if config["start_admin"] == "yes":
            self.window.mainloop()
            Logs.info_message(message + "Admin is turned ON.")
        else:
            Logs.info_message(message + "Admin is turned off.")
