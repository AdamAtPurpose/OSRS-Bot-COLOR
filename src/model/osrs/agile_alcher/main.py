import shutil
import time
from pathlib import Path

from random import randint
import utilities.api.item_ids as item_ids
import utilities.color as clr
import utilities.game_launcher as launcher
from model.bot import BotStatus
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


from model.osrs.agile_alcher.alching import execute_alchemy_actions
from model.osrs.agile_alcher.player_state import PlayerState
from model.osrs.agile_alcher.movement import execute_agility_action
from model.osrs.agile_alcher.waiting import wait_to_alch

class AgileAsHeckBoii(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "Agile Alchemy"
        description = (
            "lmao"
            " button on the right."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time: int = 20
        self.loot_items: str = ""
        self.hp_threshold: int = 0
        self.options_set = True

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return

        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully. Please launch RuneLite with the button on the right to apply settings.")

        self.options_set = True

    def launch_game(self):
        if launcher.is_program_running("RuneLite"):
            self.log_msg("RuneLite is already running. Please close it and try again.")
            return
        # Make a copy of the default settings and save locally
        src = launcher.runelite_settings_folder.joinpath("osrs_settings.properties")
        dst = Path(__file__).parent.joinpath("custom_settings.properties")
        shutil.copy(str(src), str(dst))
        # Modify the highlight list
        loot_items = self.capitalize_loot_list(self.loot_items, to_list=False)
        with dst.open() as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith("grounditems.highlightedItems="):
                lines[i] = f"grounditems.highlightedItems={loot_items}\n"
        with dst.open("w") as f:
            f.writelines(lines)
        # Launch the game
        launcher.launch_runelite_with_settings(self, dst)

    def main_loop(self):
        # Setup
        api_morg = MorgHTTPSocket()
        api_status = StatusSocket()
        start_time = time.time()
        end_time = start_time + (self.running_time * 60)

        api_morg.get_player_position

        self.player_state = PlayerState()

        while end_time - time.time() > 0 :
            time_remain = end_time - time.time()
            self.log_msg(f"time remianing: {time_remain}")
            self.update_progress((time.time() - start_time) / end_time)

            # log position
            time.sleep(0.2)

            position=api_morg.get_player_position()
            self.log_msg(f"Position: {position}")
            px,py,z = position

            if z == 1 or z == 2 or z ==3:

                #Yellow

                if px <= 2730 and px >= 2721:
                    if py>=3490 and py <= 3497:


                        red_rectangle = self.get_nearest_tag(clr.RED)

                        if red_rectangle and self.rect_is_close_to_window_center(red_rectangle, 200):

                            red_rectangle.set_rectangle_reference(self.win.game_view)
                            self.click_rectangle(red_rectangle)
                            self.player_state.get_fatigued_delay(2246)
                            execute_alchemy_actions(self, self.player_state, 34, 11, api_status, api_morg, False)
                            self.player_state.get_fatigued_delay(1000)
                        else:
                            yellow_rectangle = self.get_nearest_tag(clr.YELLOW)
                            self.player_state.get_fatigued_delay(29)
                            self.click_rectangle(yellow_rectangle)
                            self.player_state.get_fatigued_delay(3200)
                
                #Green
                if px <= 2713 and px >= 2705:
                    if py >=3488 and py <= 3495:

                        red_rectangle = self.get_nearest_tag(clr.RED)

                        if red_rectangle and self.rect_is_close_to_window_center(red_rectangle, 300):

                            red_rectangle.set_rectangle_reference(self.win.game_view)
                            self.click_rectangle(red_rectangle)
                            self.player_state.get_fatigued_delay(253)
                            execute_alchemy_actions(self, self.player_state, 34, 11, api_status, api_morg, False)
                            self.player_state.get_fatigued_delay(444)
                        else:

                            execute_alchemy_actions(self, self.player_state, 34, 11, api_status, api_morg, False)
                            green_rectangle = self.get_nearest_tag(clr.GREEN)
                            self.player_state.get_fatigued_delay(29)
                            self.click_rectangle(green_rectangle)
                            self.player_state.get_fatigued_delay(2746)
                
                #BLUE
                if px <= 2715 and px >= 2710:
                    if py >=3477 and py <= 3481:

                        red_rectangle = self.get_nearest_tag(clr.RED)

                        if red_rectangle and self.rect_is_close_to_window_center(red_rectangle, 300):

                            red_rectangle.set_rectangle_reference(self.win.game_view)
                            self.click_rectangle(red_rectangle)
                            self.player_state.get_fatigued_delay(253)
                            execute_alchemy_actions(self, self.player_state, 34, 11, api_status, api_morg, False)
                            self.player_state.get_fatigued_delay(444)
                        else:
                            execute_alchemy_actions(self, self.player_state, 34, 11, api_status, api_morg, False)
                            time.sleep(0.2)
                            blue_rectangle = self.get_nearest_tag(clr.BLUE)
                            self.click_rectangle(blue_rectangle)

                            self.player_state.get_fatigued_delay(1546)
                        self.player_state.maybe_take_break()

                #PURPLE       
                if px <= 2715 and px >= 2700:
                    if py >=3470 and py <= 3475:


                        execute_alchemy_actions(self, self.player_state, 34, 11, api_status, api_morg, False)
                        purple_rectangle = self.get_nearest_tag(clr.PURPLE)
                        self.click_rectangle(purple_rectangle)

                        self.player_state.get_fatigued_delay(1616)
                
                #CYAN
                if py<=3465:

                    red_rectangle = self.get_nearest_tag(clr.RED)
                    cyan_rectangle = self.get_nearest_tag(clr.CYAN)

                    if red_rectangle and self.rect_is_close_to_window_center(red_rectangle, 200):
                        
                        red_rectangle.set_rectangle_reference(self.win.game_view)
                        self.click_rectangle(red_rectangle)
                        self.player_state.get_fatigued_delay(500)

                    else:

                       self.click_rectangle(cyan_rectangle)
                    
                       self.player_state.get_fatigued_delay(1846)
                    
                    self.player_state.maybe_take_break()
            
            else:
                #on the ground
                
                #get all green tiles
                green_tiles = self.get_all_tagged_in_rect(rect = self.win.game_view,color = clr.GREEN)
                #sort by y coordinate on screen
                best_tile = green_tiles[0]
                min_y = green_tiles[0]._y_max

                for tile in green_tiles:
                    if tile._y_max < min_y:
                        min_y = tile._y_max
                        best_tile = tile
                self.mouse.move_to(best_tile.random_point(), mouseSpeed="fastest")
                self.mouse.click()
                #alch
                if api_morg.get_player_position()[2] == 0:
                    execute_alchemy_actions(self, self.player_state, 34, 11, api_status, api_morg, False)

                wait_to_alch(self,api_status,api_morg)



        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)
    
    def click_rectangle(self, rectangle):
        if rectangle is None:
            return
        clicks = self.player_state._get_num_clicks()

        self.mouse.move_to(rectangle.random_point(), mouseSpeed="fast")
        self.mouse.click()
        for _ in range(0,clicks-1):
            self.mouse.move_to(rectangle.random_point(), mouseSpeed="fastest")
            self.mouse.click()
    
    def rect_is_close_to_window_center(self,rectangle, tolerance):

        rectangle.set_rectangle_reference(self.win.game_view)
        return rectangle.distance_from_rect_center() < tolerance
