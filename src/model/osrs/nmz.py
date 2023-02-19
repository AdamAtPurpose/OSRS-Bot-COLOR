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


class OSRSNMZ(OSRSBot):
    def __init__(self):
        bot_title = "nmz"
        description = "nmz"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 20
        self.take_breaks = False
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
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()

        #HELPERS
        def color_nav_minimap(color: clr.Color):

            rectangle = self.get_all_tagged_in_rect(rect = self.win.minimap_area, color =  color)[0]

            for _ in range(random.randint(1,3)):
                self.mouse.move_to(rectangle.random_point(), mouseSpeed="fast")
                self.mouse.click()

        #go down
        def color_nav(color: clr.Color):
            rectangle = self.get_nearest_tag(color)

            for _ in range(random.randint(3,5)):
                self.mouse.move_to(rectangle.random_point(), mouseSpeed="medium")
                self.mouse.click()
        
        def sleep_time():
            sleep_time = random.randint(2654,6234)
            time.sleep(sleep_time)
        t0 = time.time()
        #MAIN LOOP
        while True and (time.time() - t0 < 216,000):
            
            #click rock cake
            absorbtions = [item_ids.ABSORPTION_1, item_ids.ABSORPTION_2, item_ids.ABSORPTION_3, item_ids.ABSORPTION_4]
            rock_cake = [item_ids.ROCK_CAKE]
            
            hp = api_m.get_hitpoints()
            in_combat = api_m.get_is_in_combat()
            absorbtion_index = api_m.get_inv_item_indices(absorbtions)[0]
            rock_cake_index = api_m.get_inv_item_indices(rock_cake)[0]
            
            
            self.log_msg(f"hp {hp}, in_combat{in_combat}, absorbtion_index {absorption_index}")

            if True:
                ind = absorbtion_index
                inventory_slot = self.win.inventory_slots[ind]
                for _ in range(1,3):
                    absorbtion_index = api_m.get_inv_item_indices(absorbtions)[0]
                    time.sleep(random.randint(23,57)/1000)
                    self.mouse.move_to(inventory_slot.random_point())
                    self.mouse.click()
                    time.sleep(random.randint(23,89)/1000)

            if hp >= 4:
                ind = rock_cake_index
                inventory_slot = self.win.inventory_slots[ind]
                for _ in range(1,3):
                    time.sleep(random.randint(23,57)/1000)
                    self.mouse.move_to(inventory_slot.random_point())
                    self.mouse.click()
            
            sleep_time()

            break

            
                


    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)

