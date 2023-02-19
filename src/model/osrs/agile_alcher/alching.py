import shutil
import time
from pathlib import Path

from random import randint
import utilities.api.item_ids as item_ids
import utilities.color as clr
import utilities.game_launcher as launcher
from utilities.control_panel import MagicOpen, InvOpen
from utilities.random_util import random_chance

from model.bot import BotStatus
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from model.osrs.agile_alcher.player_state import PlayerState
from model.osrs.agile_alcher.waiting import wait_to_alch

def _okay_to_alch(bot_control: OSRSBot, spell_location: int,item_location: int, api_status: StatusSocket, api_morg: MorgHTTPSocket) -> bool:
        #check spot 10
        inventory = api_status.get_inv()
        found = False
        for item in inventory:
            if item['index'] == 11:
                found = True

        if not found:
            bot_control.log_msg("No items in the right spot cant alch")
            return False

        nats = api_status.get_inv_item_indices(item_id = 561)
        if len(nats) == 0:
            bot_control.log_msg("No Natty runes can't alch")
            return False

        return True


def _generate_alching_actions(wait_for_animation: bool) -> list:
    """
    Generates a list of actions to alch items.

    Algorithm:
        1. Move to spell icon
        2. click spell
        3. move to item
        4. click item

        Optionally insert the animation waiting at any point except after 4. click item

    Returns:
        A list of actions to alch items.
    """
    actions = ['move_to_spell_icon', 'click_spell_icon', 'move_to_item', 'click_item']
    
    #sometimes wait at index 1 sometimes wait at index 2
    if wait_for_animation:
        insertion_index = 3
        actions.insert(insertion_index, 'wait_for_animation')

    return actions

def execute_alchemy_actions(bot_control: OSRSBot,player_state: PlayerState, spell_location: int,item_location: int, api_status: StatusSocket, api_morg: MorgHTTPSocket, wait_for_animation = True):
    """
    execute all actions
    """

    if random_chance(bot_control.player_state.chance_to_not_alch(0.1)):
        #sometimes we just dont bother alching idk why!
        return False

    spell_location = bot_control.win.spellbook_normal[spell_location]
    item_location = bot_control.win.inventory_slots[item_location]
    
    if _okay_to_alch(bot_control , spell_location, item_location, api_status, api_morg) == False:
        return 1

    actions = _generate_alching_actions(wait_for_animation)


    for action in actions:
        
        if action == "move_to_spell_icon":
            _move_to_spell_icon(bot_control, spell_location)
        
        elif action == "click_spell_icon":
            bot_control.mouse.click()

        elif action == "move_to_item":
            _move_to_item(bot_control, item_location)
        
        elif action == "click_item":
            _click_item(bot_control, item_location)

        elif action == "wait_for_animation":
            _wait_for_animation(bot_control, api_status, api_morg)
        else:
            raise ValueError(f"Invalid action: {action}")
    
    return 0

def _move_to_spell_icon(bot_control: OSRSBot, spell_location: int):
    """
    Move to spell icon
    """
    #ensure spell tab is open
    with MagicOpen(bot_control):
        time.sleep(0.1)
        bot_control.mouse.move_to(spell_location.random_point(), mouseSpeed="fast")

def _move_to_item(bot_control: OSRSBot, item_location: int):
    """
    Move to item
    """

    time.sleep(0.1)
    with InvOpen(bot_control):
        bot_control.mouse.move_to(item_location.random_point(), mouseSpeed="fast")  

def _click_item(bot_control: OSRSBot, item_location):
    """
    Click item
    """
    bot_control.mouse.click()

def _wait_for_animation(bot_control: OSRSBot, api_status: StatusSocket, api_morg: MorgHTTPSocket):
    """
    Wait for animation
    """
    wait_to_alch(bot_control, api_status, api_morg)