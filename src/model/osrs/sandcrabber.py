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


class OSRSandcrab(OSRSBot):
    def __init__(self):
        bot_title = "sandcrab"
        description = "does sandcrabs in the laziest way possible"
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
            sleep_time = random.randint(3412,5723)/1000
            time.sleep(sleep_time)

        #MAIN LOOP
        while True:

            self.log_msg(f"position{api_m.get_player_position()}")
            cyan_rect = self.get_nearest_tag(clr.CYAN)
            for _ in range(random.randint(1,3)):
                self.mouse.move_to(cyan_rect.random_point(), mouseSpeed="fast")
                self.mouse.click()

            sleep_time()
            

            att_pots = [item_ids.ATTACK_POTION1, item_ids.ATTACK_POTION2,item_ids.ATTACK_POTION3, item_ids.ATTACK_POTION4]
            for pot in str_pots:
                potion_index = api_s.get_inv_item_indices(pot)
                if potion_index:
                    break

            if potion_index:
                ind = potion_index[0]
                inventory_slot = self.win.inventory_slots[ind]
                self.mouse.move_to(inventory_slot.random_point())
                self.mouse.click()

            red_rectangle = self.get_nearest_tag(clr.RED)
            for _ in range(random.randint(1,3)):
                self.mouse.move_to(red_rectangle.random_point(), mouseSpeed="fast")
                self.mouse.click()

            sleep_time()
            count_not_in_combat = 0

            t0 = time.time()
            while count_not_in_combat < 3:

                ret = api_m.get_is_in_combat()

                if ret == False:
                    count_not_in_combat += 1
                else:
                    count_not_in_combat = 0
                

                if time.time() - t0 > 5:
                    position = api_m.get_player_position()
                    if position != (1764, 3445, 0):
                        self.log_msg(f"correcting positions")
                        red_rectangle = self.get_nearest_tag(clr.RED)
                        self.mouse.move_to(red_rectangle.random_point(), mouseSpeed="fast")
                        self.mouse.click()
                        t0 = time.time()
                    if time.time() - t0 > random.randint(45,60):
                        self.log_msg("ensuring I dont log out")
                        self.mouse.move_to(self.win.game_view.random_point())
                        t0 = time.time()
                
                sleep_time()
                
            
            self.log_msg("Not in combat! time to run a bit.")

            sleep_time()

            t0 = time.time()
            start = api_m.get_player_position()
            self.log_msg(f"starting position {start}")
            while time.time()-t0 < 10:

                self.log_msg("down..")
                color_nav(clr.BLUE)
                sleep_time()
                color_nav_minimap(clr.BLUE)
                sleep_time()


            bottom = api_m.get_player_position()

            self.log_msg(f"bottom position {bottom}")
            t1 = time.time()
            while time.time() - t1 < 5:
                self.log_msg("up...")
                color_nav_minimap(clr.GREEN)
                sleep_time()
                color_nav(clr.GREEN)
                sleep_time()

            str_pots = [item_ids.STRENGTH_POTION1, item_ids.STRENGTH_POTION2,item_ids.STRENGTH_POTION3, item_ids.STRENGTH_POTION4]
            att_pots = [item_ids.ATTACK_POTION1, item_ids.ATTACK_POTION2,item_ids.ATTACK_POTION3, item_ids.ATTACK_POTION4]
            for pot in str_pots:
                potion_index = api_s.get_inv_item_indices(pot)
                if potion_index:
                    break

            if potion_index:
                ind = potion_index[0]
                inventory_slot = self.win.inventory_slots[ind]
                self.mouse.move_to(inventory_slot.random_point())
                self.mouse.click()
            
                


    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)

