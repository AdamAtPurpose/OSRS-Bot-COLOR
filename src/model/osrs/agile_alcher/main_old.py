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
        # Setup
        api_morg = MorgHTTPSocket()
        api_status = StatusSocket()
        player_state = PlayerState()
        start_time = time.time()
        end_time = self.running_time * 60

        while time.time() - start_time < end_time:

            #take next action
            color_cycle = [clr.YELLOW, clr.GREEN, clr.BLUE, clr.PURPLE]
            color_names = ["Yellow", "Green", "Blue", "Purple"]
            for color,color_name in zip(color_cycle,color_names):

                self.log_msg(f"Starting {color_name} cycle")

                action = execute_agility_action(
                bot_control = self,
                api_morg = api_morg,
                api_status = api_status,
                player_state = player_state,
                color = color)

                if action == 1:
                    wait_to_alch(self,api_status, api_morg)
                    break
                if action == 2:
                    player_state.get_fatigued_delay(38)
                    action = execute_agility_action(
                    bot_control = self,
                    api_morg = api_morg,
                    api_status = api_status,
                    player_state = player_state,
                    color = color)

                    if action == 1:
                        wait_to_alch(self,api_status, api_morg)
                        break

                #execute alchemy random action ordering is created here and automatically waits for a time to cast
                if execute_alchemy_actions(
                    bot_control = self,
                    player_state = player_state,
                    spell_location = 34,
                    item_location = 11,
                    api_status = api_status,
                    api_morg = api_morg
                    ) == 1:
                    
                    wait_to_alch(self,api_status, api_morg)

            self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.set_status(BotStatus.STOPPED)