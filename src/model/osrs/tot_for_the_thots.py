import time
import random
from utilities.api import item_ids

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject


class TotThot(OSRSBot):
    def __init__(self):
        bot_title = "Tot Thot 1.0"
        description = "slays that hot tot thot"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 20
        self.options_set = True


    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Setup API
        t0 = time.time()
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()


        while time.time() - t0 < self.running_time:
            # OCR example
            hp = api_m.get_hitpoints()
            animation = api_m.get_animation_id()
            animation_id = api_m.get_animation_id()
            
            self.log_msg(f"hp: {hp}, animation: {animation} , animation_id : {animation_id}")
            time.sleep(2)


            
