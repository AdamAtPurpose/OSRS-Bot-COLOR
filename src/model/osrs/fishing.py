import time

import pyautogui as pag
import random
import utilities.api.item_ids as ids
import utilities.color as clr
from model.bot import BotStatus
from model.osrs.osrs_bot import OSRSBot
from utilities.api.status_socket import StatusSocket
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.geometry import Point, RuneLiteObject, Rectangle
from utilities.ocr import PLAIN_11, find_text , extract_text
from utilities.random_util import random, random_chance


class NRFishing(OSRSBot):
    def __init__(self):
        title = "Fishing"
        description = "This bot fishes... fish. Position your character near a tagged fishing spot, and press play."
        super().__init__(bot_title=title, description=description)
        self.running_time = 2

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Bot will run for {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def sort_inv_indices(self, indices):
        output = []

        for remainder in range(0,4):
            for index in indices:
                if index % 4 == remainder:
                    output.append(index)
        
        return output
    
    def log_in(self, acc: dict):
        self.log_msg("Logging in")
        self.mouse.move_to((2458,525))
        self.mouse.click()
        for i in range(0,30):
            pag.keyDown('backspace')
            pag.keyUp('backspace')

        pag.keyDown("tab")
        pag.keyUp("tab")
        for i in range(0,30):
            pag.keyDown('backspace')
            pag.keyUp('backspace')

        pag.write(acc['u'])

        pag.keyDown("tab")
        pag.keyUp("tab")

        pag.write(acc['p'])

        pag.keyDown("enter")
        pag.keyUp("enter")
        time.sleep(15)
        pag.click()

    def swap_acc(self, acc_1, acc_2, curr_acc):
        self.log_msg("Time to log out")
        self.logout()
        time.sleep(10)
        new_acc = acc_1 if curr_acc == acc_2 else acc_2
        curr_acc = new_acc
        self.log_in(new_acc)
        time.sleep(5)
        start_time = time.time()
        prelog = random.randint(120,3600)
        return curr_acc

    def main_loop(self):  # sourcery skip: low-code-quality, use-named-expression
        
        acc_1 = {
            'u':'BurritoDan123@gmail.com' ,
            'p': 'POOpooPEEpeetime123'
        }

        acc_2 = {
            'u':'shanto@panto.xom' ,
            'p': 'ShantoPanto42069'
        }
        curr_acc = acc_1
        # API setup
        api = StatusSocket()
        #self.log_msg("Selecting inventory...")
        #self.mouse.move_to(self.win.cp_tabs[3].random_point())
        #self.mouse.click()
        morg = MorgHTTPSocket()
        fished = 0
        failed_searches = 0
        game_center = self.win.game_view.get_center()
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        end_time_abs = self.running_time * 60 + time.time()
        prelog = random.randint(120, 6000)
        while time.time() - start_time < end_time:

            self.log_msg(f"time remain {end_time_abs - time.time() - prelog}")
            self.log_msg(f"time from the end we're taking off, {prelog}")
            feathers = api.get_inv_item_stack_amount(ids.FEATHER)
            
            if feathers < 15:
                self.update_progress(1)
                self.log_msg("Finished.")
                self.logout()
                self.set_status(BotStatus.STOPPED)

            try:
                spot = self.get_nearest_tag(clr.FISHING_SPOT_CYAN)
                spot.set_rectangle_reference(self.win.game_view)
                spot = find_text(text = "Trou" ,rect = spot.rect, font = PLAIN_11, color = clr.FISHING_SPOT_CYAN)[0]
                spot.height = spot.height*10

            except Exception as e:
                    print(e)
                    time.sleep(6)

            #text = extract_text(rect = spot.rect, font = PLAIN_11, color = clr.FISHING_SPOT_CYAN)
            #self.log_msg(f"Extracted the follwoing {text}")
            
            raw_fish = api.get_inv_item_indices(ids.raw_fish)
            raw_fish = self.sort_inv_indices(raw_fish)
            self.log_msg(f"raw fish indices {raw_fish}")
            # Check to drop inventory
            DROP_COMBO_1 = [0,4,1,5,2,6]
            drop_combo = all([index in raw_fish for index in DROP_COMBO_1])
            if len(raw_fish) > 8 and random_chance(0.5) or len(raw_fish) >=21:
                chance = random.randint(1,26)
                self.log_msg(f"rolled a {chance} change with {len(raw_fish)} indices full")
                if chance > len(raw_fish):
                    pass
                else:
                    if drop_combo and random_chance(0.8) == 1:
                        self.drop(slots = DROP_COMBO_1)
                    else:
                        raw_fish = self.sort_inv_indices(raw_fish)
                        self.drop(slots=raw_fish[:random.randint(8,len(raw_fish))])
                        fished += len(raw_fish)
                        self.log_msg(f"Fishes fished: ~{fished}")

            # If not fishing, click fishing spot
            while not self.is_player_doing_action("Fishing"):
                try:
                    spot = self.get_nearest_tag(clr.FISHING_SPOT_CYAN)
                    spot.set_rectangle_reference(self.win.game_view)
                    spot = find_text(text = "Trou" ,rect = spot.rect, font = PLAIN_11, color = clr.FISHING_SPOT_CYAN)[0]

                    spot.height = spot.height*10
                except Exception as e:
                    print(e)
                    time.sleep(10)
                self.log_msg(f"nearest tag: {spot}")
                if spot is None:
                    failed_searches += 1
                    time.sleep(2)
                    if failed_searches > 10:

                        self.log_msg("Failed to find fishing spot.")
                        curr_acc = self.swap_acc(acc_1,acc_2, curr_acc)
                        start_time = time.time()
                        prelog = random.randint(120,3600)

                else:
                    self.log_msg("Clicking fishing spot...")
                    self.mouse.move_to(spot.random_point())
                    pag.click()
                    time.sleep(1)
                    self.mouse.move_to(self.win.game_view.random_point())
                    if random_chance(0.2):
                        self.mouse.move_to(spot.random_point())
                        pag.click()

                    break
            failed_searched = 0 
            ran_pt = random.randint(0,1000), random.randint(0,1000)
            self.mouse.move_to(ran_pt)
            time.sleep(6)
            self.log_msg(f"time {time.time()} end time = {end_time_abs}")
            if (end_time_abs - time.time() < prelog ):

                curr_acc = self.swap_acc(acc_1,acc_2, curr_acc)
                start_time = time.time()
                prelog = random.randint(120,3600)

            #check exp
            if random.randint(0,100) > 95:
                self.mouse.move_to(self.win.cp_tabs[1].random_point())
                self.mouse.click()
                self.mouse.move_to(self.win.inventory_slots[11].random_point())
                time.sleep(random.randint(2,4))
                self.mouse.move_to(self.win.cp_tabs[3].random_point())
                self.mouse.click()
                time.sleep(random.randint(100,300)/100)
            
            #check quests
            elif random.randint(0,100) > 95:
                self.mouse.move_to(self.win.cp_tabs[2].random_point())
                self.mouse.click()
                slot = random.randint(0,20)
                slot = slot - slot%4
                self.mouse.move_to(self.win.inventory_slots[slot].random_point())
                time.sleep(random.randint(2,4))
                self.mouse.move_to(self.win.cp_tabs[3].random_point())
                self.mouse.click()
                time.sleep(random.randint(100,300)/100)
            
            elif random.randint(0,1000) == 1:

                timeout = random.randint(60, 600)
                self.log_msg(f"fcuking off for like a bit {timeout}")
                time.sleep(timeout)


            # Update progress
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.set_status(BotStatus.STOPPED)

