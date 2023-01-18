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


class AgileAsHeckBoii(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "state_logger"
        description = (
            "This bot does nothing it just logs"
            " button on the right."
        )
        super().__init__(bot_title=bot_title, description=description)
        self.running_time: int = 20
        self.loot_items: str = ""
        self.hp_threshold: int = 0
        self.options_set = True

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 60)

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
        self.log_msg("WARNING: This script is for testing and may not be safe for personal use.")
        # Setup API
        api_morg = MorgHTTPSocket()
        api_status = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        while time.time() - start_time < end_time:

            red,green = self.gather_state(api_morg, api_status)

            #take next action
            action = self.next_agility_action(red, green, api_status)

            #watch the state
            if action == 0:
                self.alch_something(11,api_status, api_morg)
            else:
                self.log_msg("not going to alch since we just grabbed a mark")

            #time.sleep(randint(0,13)/1000)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)
    
    def _move_and_click_agility(self, spot):
        clicks = randint(1,10)
        if clicks % 3 == 0:
            clicks = 2
        elif clicks %2 == 0:
            clicks = 1
        else:
            clicks = 0

        self.mouse.move_to(spot.random_point(), mouseSpeed="fast")
        self.mouse.click()
        for i in range(clicks):
            self.mouse.move_to(spot.random_point(), mouseSpeed="fastest")
            milliseconds = randint(17,39)
            time.sleep(milliseconds / 1000)
            self.mouse.click()


    def gather_state(self, api_morg: MorgHTTPSocket , api_status: StatusSocket):
        #gather information about the player and surroundings, return a state

        #position
        position = api_morg.get_player_position() #World Point position

        #player state
        hitpoints = api_morg.get_hitpoints()
        status_api_animation = api_status.get_animation_data()
        status_api_animation_id = api_status.get_animation_id()

        if status_api_animation_id and status_api_animation:
            self.log_msg("Animation Data")
            self.log_msg(f"Status API Animation ID: {status_api_animation_id}")
            self.log_msg(f"Status API Animation: {status_api_animation}")
        #surroundings
        self.log_msg(f"Position: {position}")
        self.log_msg(f"Hitpoints: {hitpoints}")

        green = self.get_nearest_tag(clr.GREEN)
        red = self.get_nearest_tag(clr.RED)

        if green:
            self.log_msg("Logging greens")
            self.log_msg(f"distance to green: {green.distance_from_rect_center()}")
            self.log_msg(f"Green: {green.center()}")
        if red:
            self.log_msg(f"distance to red: {red.distance_from_rect_center()}")
            self.log_msg(f"Red: {red.center()}")

        return red,green

    def next_agility_action(self,red,green, api_status):
        """
        Given a rectangle for red and green location take the next action
        """

        marks = api_status.get_inv_item_stack_amount(item_id = 11849)
        self.log_msg(f"number of marks: {marks}")

        if red:
            #click red
            self._move_and_click_agility(red)
        elif red and green:
            #click the one that is closer
            if red.distance_from_rect_center() < green.distance_from_rect_center():
                #red
                self._move_and_click_agility(red)
            else:
                #green
                self._move_and_click_agility(green)
                return 1
        elif green:
            #click green
            self._move_and_click_agility(green)
            time.sleep(randint(27,127)/1000)

            #might just fuckin take a break rn tbh
            if randint(0,100) < 37:
                sleeptime = randint(25,137)
                self.log_msg(f"Taking a break... {sleeptime}")
                time.sleep(sleeptime)

            return 1
        else:
            self.log_msg("No spots found")
            #quit
            raise AssertionError("No Actions Found")

        time.sleep(randint(27,127)/1000)
        marks_after = api_status.get_inv_item_stack_amount(item_id = 11849)

        if marks_after != marks:
            self.log_msg(f"Mark gained: {marks_after - marks}")
            return 1
        
        return 0

        
    
    def wait_for_animation(self, api_status: StatusSocket, api_morg: MorgHTTPSocket):
        animation_id = api_status.get_animation_id()
        start_time = time.time()
        positions = []
        positions.append(api_morg.get_player_position())
        if animation_id == -1:
            self.log_msg("Waiting for animation to begin...")
            while animation_id == -1:
                animation_id = api_status.get_animation_id()
                positions.append(api_morg.get_player_position())

                if animation_id == -1 and len(positions) >= 2:
                    if positions[-1] == positions[-2]:
                        self.log_msg("Animation Start: No movement detected")
                        time.sleep(0.3)
                        break
                time.sleep(0.3)
                if time.time() - start_time > 9:
                    self.log_msg("Animation Start: Timeout continuing")
                    return 1
            
        self.log_msg(f"Animation detected: Status API Animation ID: {animation_id}")

        animation_id = api_status.get_animation_id()

        if animation_id != -1:
            while animation_id != -1:
                self.log_msg(f"Runtime Sleep: Status API Animation ID: {animation_id}")
                animation_id = api_status.get_animation_id()
                time.sleep(0.2)
                if time.time() - start_time > 9:
                    self.log_msg("Animation End: Timeout Continueing")
                    return 1
        self.log_msg("Animation Tracker: Start and finish detected")
        return 0
    

    def alch_something(self,item_to_alch, api_status: StatusSocket, api_morg: MorgHTTPSocket):
        """
        Alch something
        """
        spell_location = self.win.spellbook_normal[34]
        item_location = self.win.inventory_slots[11]
        #check spot 10
        inventory = api_status.get_inv()
        found = False
        for item in inventory:
            if item['index'] == 11:
                self.log_msg("Found items in the right spot")
                found = True

        if not found:
            self.log_msg("No items in the right spot")
            self.wait_for_animation(api_status, api_morg)
            return 0
        nats = api_status.get_inv_item_indices(item_id = 561)
        if len(nats) == 0:
            self.log_msg("No Natty runes")

            self.wait_for_animation(api_status, api_morg)
            return 0
        self.log_msg(f"nature runes {nats}")

        #time to alch
        self.mouse.move_to(spell_location.random_point(), mouseSpeed="medium")
        time.sleep(randint(7,13)/1000)
        self.mouse.click()

        moved = False

        if randint(0,100)> 25:
            moved = True
            for i in range(0,randint(1,3)):
                self.mouse.move_to(item_location.random_point(), mouseSpeed="fastest")

        #Wait for animation to complete
        self.wait_for_animation(api_status, api_morg)
        if moved == False:
            for i in range(1,randint(1,3)):
                self.mouse.move_to(item_location.random_point(), mouseSpeed="fastest")
        time.sleep(randint(13,53)/1000)
        self.mouse.click()

        return 1
                