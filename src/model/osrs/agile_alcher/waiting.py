
import time
from random import randint
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import math

def wait_to_alch_old(bot_control, api_status: StatusSocket, api_morg: MorgHTTPSocket):
    """
    breaks when no movement is detected
    """
    positions = []
    positions.append(api_morg.get_player_position())
    movement = False

    while movement == True:

        position = api_morg.get_player_position()
        positions.append(position)
        
        #check movement state
        if len(positions) >=2:
            if positions[-1] == positions[-2]:
                #were not moving
                movement = False
                break
        
        time.sleep(0.91)

    return 0

def wait_to_alch(bot_control, api_status: StatusSocket, api_morg: MorgHTTPSocket):
    """
    No animations and no movement
    """
    animation_id = api_status.get_animation_id()
    positions = []
    positions.append(api_morg.get_player_position())

    animation_start, animation_end, movement = False, False, True

    while movement == True or (animation_start == False and animation_end ==False):

        animation_id = api_status.get_animation_id()
        position = api_morg.get_player_position()
        positions.append(position)

        bot_control.log_msg(f"Waiting to be idle... animation: {animation_id}, position: {position}")


        if animation_start == False:
            if animation_id != -1 and animation_id != 713:
                animation_start = True
        elif animation_start == True and animation_id == -1:
            animation_end = True
        
        #check movement state
        if len(positions) >=2:

            if math.dist(positions[-1], positions[-2]) <= 1.5 :            
                return 0


            if positions[-1] == positions[-2]:
                #were not moving
                movement = False
         
        if movement == False:
            bot_control.log_msg("movement has halted")
            break
        
        if animation_start == animation_end == True:

            bot_control.log_msg("animation_halted")
            break

    return 0
