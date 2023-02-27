import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject, Point
from utilities.imagesearch import search_img_in_rect
from pathlib import Path
import pyautogui as pag
from utilities.random_util import truncated_normal_sample, chisquared_sample, random_chance
from utilities.api.item_ids import BURNT_LOBSTER
import math
import random



class OSRSBankStander(OSRSBot):
    def __init__(self):
        bot_title = "Bank Stander"
        description = "stands at the bank"
        super().__init__(bot_title=bot_title, description=description)
        self.options_set = True

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        self.options_set = True
    

    def wait_to_alch(self, api_status: StatusSocket, api_morg: MorgHTTPSocket):
        """
        No animations and no movement
        """
        positions = []
        positions.append(api_morg.get_player_position())

        movement = True

        while movement == True:
            time.sleep(0.6)
            position = api_morg.get_player_position()
            self.log_msg(f"player position {position}")
            positions.append(position)

            self.log_msg(f"Waiting to be not moving... position: {position}")

            #check movement state
            if len(positions) >=2:

                if positions[-1] == positions[-2]:
                    #were not moving
                    movement = False
        self.log_msg(f"Exiting now due to following movements {positions}")
        return 0


    def midpoints(self) -> list:


        points = []

        all_rect = self.get_all_tagged_in_rect(self.win.game_view,clr.YELLOW)
        self.log_msg(f"Rectangles Found: {len(all_rect)}")
        rect = all_rect[random.randint(0,len(all_rect) - 1)]
        #random points
        points.append(rect.random_point())
        rect = self.get_nearest_tag(clr.YELLOW)
        self.log_msg(f"sorted points = {points}")

        return points       

    def cook(self, api_m, api_s, raw_fish_id):
        
        rect = None
        self.log_msg("Looking for a blue tag")
        mid_points = self.midpoints()
        while rect is None:
            self.log_msg(f"Searching for a blue tag...")
            rect = self.get_nearest_tag(clr.BLUE)
        
        self.log_msg(f"mouseover text contains Range or range: {self.mouseover_text(contains = ['Range', 'range'])}")
        if random_chance(0.8):
            for point in mid_points:
                #move midpoint towards blue center

                blue_center = rect.random_point()
                self.log_msg(f"interpolating between two points yellow {point}, blue: {blue_center}")
                dx = point.x - blue_center.x
                dy = point.y - blue_center.y

                self.log_msg(f'dx: {dx}. dy: {dy}')

                self.log_msg(f"new x {point.x} - {dx} * 0.5")
                self.log_msg(f"new y {point.y} - {dy} * 0.5")

                x = point.x - dx*0.5
                y = point.y - dy*0.5

                new_point = Point(int(x),int(y))
                self.log_msg(f"After interpolation | yellow: {new_point}")

                self.mouse.move_to(new_point, speed = "fastest")
                self.mouse.click()

        while not self.mouseover_text(contains = ['Range', 'range', "Rang", "rang", "cook", "Cook"]):
            try:
                self.mouse.move_to(rect.random_point())
                self.log_msg(f"Mouseover while looking for range: {self.mouseover_text()}")
                rect = self.get_nearest_tag(clr.BLUE)
            except AttributeError:
                self.log_msg("Can't find blue range rectangle")
                return

        self.mouse.click()

        num_raw_fish = len(api_m.get_inv_item_indices(raw_fish_id))
        #run over
        self.wait_to_alch(api_s,api_m)
        time.sleep(truncated_normal_sample(0.5,2.5))
        # spacebar
        count = 0
        while num_raw_fish == len(api_m.get_inv_item_indices(raw_fish_id)):
            if count >= 2:
                return 
            self.log_msg(f"tapping spacebar...")
            for i in range(0, random.randint(1,4)):
                time.sleep(truncated_normal_sample(0.2,1))
                pag.keyDown('space')
                time.sleep(random.uniform(0.2,0.5))
                pag.keyUp('space')
            count += 1
        readings = []
        while len(api_m.get_inv_item_indices(raw_fish_id)) > 0:

            time.sleep(2)
            num_raw_fish = len(api_m.get_inv_item_indices(raw_fish_id))
            readings.append(num_raw_fish)
            if len(readings) >=3:
                if readings[-1] == readings[-2] == readings[-3]:
                    self.log_msg("stopped cooking exiting the cooking loop")
                    return

            if num_raw_fish in [1,2,3]:
                if random_chance(0.2):
                    rect = self.get_nearest_tag(clr.RED)
                    self.mouse.move_to(rect.random_point())



    def go_to_bank(self, deposit_button):

        #click bank
        count = 0 
        rect = None
        try:
            while rect is None:
                rect = self.get_nearest_tag(clr.RED)
                time.sleep(0.3)

            while not self.mouseover_text(contains = ['Bank', 'Booth']):
                if count > 5:
                    return 
                count += 1
                rect = self.get_nearest_tag(clr.RED)
                self.mouse.move_to(rect.random_point(), speed= "fastest")

            self.mouse.click()

            if deposit_button:
                self.log_msg("Premoving to deposit button last location")
                self.mouse.move_to(deposit_button.random_point())
            self.log_msg("Clicked on bank, relinquishing control to runtime")
        except AttributeError as e:
            self.log_msg(f"Error going to bank: {e}")
            pass



    def bank(self, api_m: MorgHTTPSocket):

        __PATH = Path(__file__).parent.parent.parent.parent
        SCRAPER_IMAGES = __PATH.joinpath("images", "bot", "scraper")

        raw_salmon_path = SCRAPER_IMAGES.joinpath("Lobster_bank.png")
        deposit_all_path = SCRAPER_IMAGES.joinpath("deposit_all.png")
        deposit_button = None
        count = 0
        #deposit all
        try:
            if api_m.get_is_inv_full():
                if random_chance(0.80):
                    deposit_button = None
                    while deposit_button is None:
                        if count > 5:
                            self.log_msg("couldnt find deposit button")
                            return
                        count += 1
                        self.log_msg("looking for deposit all button")
                        deposit_button = search_img_in_rect(deposit_all_path, self.win.game_view)
                    
                    count = 0

                    while not self.mouseover_text(contains = ['Deposit', 'inventory']):
                        if count > 5:
                            self.log_msg(f"couldnt find mousover text for deposit button")
                            return
                        count+=1
                        self.log_msg("moving to deposit all button")
                        self.mouse.move_to(deposit_button.random_point(), speed = "fastest")
                    self.mouse.click()

                else:
                    # or click lobster
                    inv_spot = self.win.inventory_slots[random.randint(0,3)*4].random_point()
                    self.mouse.move_to(inv_spot)
                    self.mouse.click()

                    # check for burn
                    self.log_msg(f"These items remain {api_m.get_if_item_in_inv(BURNT_LOBSTER)}")



            #withdraw salmon
            rect = None
            while rect is None:
                self.log_msg("looking for raw fish...")
                rect = search_img_in_rect(raw_salmon_path, self.win.game_view)
            while not self.mouseover_text(contains = ['Rawlobster', 'lobster']):
                self.log_msg("moving to raw fish...")
                self.mouse.move_to(rect.random_point(), speed = "fastest")
            self.log_msg("click")
            self.mouse.click()
            time.sleep(0.9)

        except AttributeError as e:
            self.log_msg(f"ERROR {e}: Continuing")
        
        return deposit_button
    
    def main_loop(self):
        # Setup API
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()
        failure_count = 0

        deposit_button = None
        
        COOKED_FISH = 379
        RAW_FISH = 377

        #basic setup
        time.sleep(1)
        while True:
            self.log_msg(f"Runtime tick")

            #state
            player_animation_id = api_m.get_animation_id()

            num_raw_fish = len(api_m.get_inv_item_indices(RAW_FISH))
            num_cooked_fish = len(api_m.get_inv_item_indices(COOKED_FISH))

            bank_rectangle = self.get_nearest_tag(clr.RED)
            range_rectangle = self.get_nearest_tag(clr.BLUE)

            self.log_msg(f"animation = {player_animation_id} , num raw fish: {num_raw_fish}, num_cooked_fish = {num_cooked_fish}")

            if num_raw_fish == 0 and bank_rectangle is not None:
                self.log_msg(f"No raw fish time to bank")
                self.go_to_bank(deposit_button)
                self.log_msg("Going to wait for movement to discontinue now...")
                self.wait_to_alch(api_s,api_m)


            elif num_raw_fish != 0 and range_rectangle:
                self.log_msg(f"time to cook")
                self.cook(api_m, api_s, RAW_FISH)

                #after cooking we chill sometimes idek
                sleeptime = chisquared_sample(1, 0.2, 15)
                self.log_msg(f"chillin after the cookout for {sleeptime}seconds")
                time.sleep(sleeptime)

            elif bank_rectangle is None:
                deposit_button = self.bank(api_m)
            else:
                failure_count += 1
                self.log_msg(f"No State Parable")
                if failure_count > 5:
                    time.sleep(1)
                    raise AssertionError("idk what to do in this state")
                else:
                    time.sleep(1)
                    continue

            failure_count = 0
            self.update_progress(1)

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

