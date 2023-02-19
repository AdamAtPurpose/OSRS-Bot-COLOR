from random import randint
import time
from model.osrs.agile_alcher.player_state import PlayerState
import utilities.color as clr
import math
from model.osrs.osrs_bot import OSRSBot
from utilities.geometry import Rectangle, RuneLiteObject
from model.osrs.agile_alcher.alching import execute_alchemy_actions
from model.osrs.agile_alcher.waiting import wait_to_alch
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.random_util import random_chance

def _move_and_click_agility(bot_control, spot: RuneLiteObject, player_state: PlayerState, color: clr.Color, ground = False):
    

    if ground:
        clicks = player_state._get_num_clicks()
        spot.set_rectangle_reference(bot_control.win.game_view)
        bot_control.log_msg(f"clicks: {clicks}")
        for _ in range(0,clicks-1):
            bot_control.mouse.move_to(spot.random_point(), mouseSpeed="fastest")
            bot_control.mouse.click()
            return True


    success = False
    count = 0

    while True:

        clicks = player_state._get_num_clicks()
        try:
            spot.set_rectangle_reference(bot_control.win.game_view)
            bot_control.log_msg(f"clicks: {clicks}")
            for _ in range(0,clicks-1):
                bot_control.mouse.move_to(spot.random_point(), mouseSpeed="fastest")
                bot_control.mouse.click()

            bot_control.mouse.move_to(spot.random_point(), mouseSpeed="fastest")
            success = bot_control.mouse.click_with_check(spot.rect)

            bot_control.log_msg(f"mouse click confirmation {success}, {count}")

            player_state.get_fatigued_delay(2123)
        except AttributeError as e:
            bot_control.log_msg(f"AttributeError: {e}")
            count += 1

        if color == clr.RED:
            _, spot, _ = _get_context(bot_control = bot_control, api_morg = None, api_status = None, color = color)
        else:
            spot, _, _ = _get_context(bot_control = bot_control, api_morg = None, api_status = None, color = color)
            if spot is None:
                bot_control.log_msg(f"We had a rectangle and now it is gone")
                success = True
         
        if count >= 5:
            bot_control.log_msg(f"count: exit")
            return False

        if success == True:
            bot_control.log_msg(f"success: exit")
            return True
        
        bot_control.log_msg(f"trying again...")

        #for _ in range(round(clicks-1)):
            #bot_control.mouse.move_to(spot.random_point(), mouseSpeed="fastest")
            #player_state.get_fatigued_delay(17)
            #successful = bot_control.mouse.click_with_check(spot.rect)
            #bot_control.log_msg(f"mouse click confirmation {successful}")
    return count >= 5


def _get_context(bot_control: OSRSBot, api_morg, api_status, color: clr.Color):
        
        if api_morg:
            x,y,z= api_morg.get_player_position() #World Point position
            red = bot_control.get_nearest_tag(clr.RED)
            color = bot_control.get_nearest_tag(color)
            return color, red, z

        else:
            red = bot_control.get_nearest_tag(clr.RED)
            color = bot_control.get_nearest_tag(color)

            return color, red, None


def _ground_actions(bot_control, api_morg, red, green, player_state, color):

    #return southernmost of the two rectangles
    if red and green:
        if red.center()[1] > green.center()[1]:
            _move_and_click_agility(bot_control, red, player_state, color = color)
        else:
            _move_and_click_agility(bot_control, green, player_state, color = color)
    elif green:
        _move_and_click_agility(bot_control,green, player_state, color = color, ground = True)
    elif red:
        _move_and_click_agility(bot_control,red, player_state, color = color)
    else:
        #are we still on the ground?
        player_state.get_fatigued_delay(53)
        _, _, z = _get_context(bot_control,api_morg, None, color)
        if z != 0:
            bot_control.log_msg("thought I was on the ground, I am not though... continuing")
            return 1
        #quit
        raise AssertionError("No Actions Found")
    
    #Ground movements take a little longer...

    if random_chance(0.8):
        execute_alchemy_actions(bot_control, player_state, 34,11,None,api_morg,False)
    player_state.get_fatigued_delay(53)

    return 1


def execute_agility_action(bot_control,api_morg,api_status, player_state: PlayerState, color: clr.Color):
    """
    Given a rectangle for red and green location take the next action
    """
    
    color_rect, red_rect, z = _get_context(bot_control, api_morg ,api_status, color)
    tries = 0

    #Wait to see something
    while color_rect == None and red_rect == None:
        color_rect, red_rect, z = _get_context(bot_control, api_morg ,api_status, color)
        tries +=1
        player_state.get_fatigued_delay(27)
        time.sleep(1)
        if tries >=10:
            bot_control.log_msg("execute_agility: No rectangles found after 10 tries")
            raise AssertionError("No Actions Found")
    
    #not on the ground and no color rectangle, maybe a red?
    #while z != 0 and color_rect is None:
        #time.sleep(0.1)
        #color_rect, red_rect, z = _get_context(bot_control, api_morg ,api_status, color)
        #tries +=1
        #if tries >= 10:
            #bot_control.log_msg("No spots found")
            ##quit
            #raise AssertionError("No Actions Found")


    #on the ground
    if z == 0 :
        color_rect, red_rect, z = _get_context(bot_control, api_morg ,api_status, clr.GREEN)
        _ground_actions(bot_control, api_morg, red_rect, color_rect, player_state, color)
        return 1

    #Mark Situation
    if color_rect and red_rect:
        get_mark(bot_control, player_state, color, api_morg, api_status)

    #only colored rectangle
    elif color_rect:
        _move_and_click_agility(bot_control = bot_control, player_state = player_state, spot = color_rect, color = color)
    else:
        bot_control.log_msg("No spots found")
        #quit
        raise AssertionError("No Actions Found")

    return 0



def get_mark(bot_control: OSRSBot, player_state: PlayerState, color: clr.Color, api_morg: MorgHTTPSocket, api_status: StatusSocket):
    color_rect, red_rect = None, None

    while color_rect is None or red_rect is None:
        color_rect, red_rect, z = _get_context(bot_control, api_morg ,api_status, clr.GREEN)
   
    game_center = bot_control.win.game_view.get_center()
    red_center= red_rect.center()
    color_center = color_rect.center()

    red_dist= math.dist([game_center.x, game_center.y], [red_center.x, red_center.y])
    color_dist = math.dist([game_center.x, game_center.y], [color_center.x, color_center.y])

    #edge case hardcoded here
    if color == clr.GREEN and z != 0:
        bot_control.log_msg("Movement: edge case handler where were on the roof with a mark thats far but should still go grab it....")
        _move_and_click_agility(bot_control, red_rect, player_state, color)
        wait_to_alch(bot_control, api_status,api_morg)
        color_rect, red_rect, z = _get_context(bot_control, api_morg ,api_status, clr.GREEN)
        _move_and_click_agility(bot_control, color_rect, player_state, color = color)


    if red_dist < color_dist:
        bot_control.log_msg("Movement: Grabbing mark, then continuing...")
        _move_and_click_agility(bot_control, red_rect, player_state, color)
        wait_to_alch(bot_control, api_status,api_morg)
        color_rect, red_rect, z = _get_context(bot_control, api_morg ,api_status, clr.GREEN)
        _move_and_click_agility(bot_control, color_rect, player_state, color = color)
        
    else:

        bot_control.log_msg("Movement: Potentially a mark detected but it's too far, continuing...")
        _move_and_click_agility(bot_control, color_rect, player_state, color = color)
