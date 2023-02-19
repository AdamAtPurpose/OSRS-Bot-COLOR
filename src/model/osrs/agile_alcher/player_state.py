import time
from random import randint
import math

class PlayerState:

    def __init__(self):
        self.t0 = time.time()
        self.last_measurement = time.time()
        #base fatigue
        self.fatigue = 1

    def get_fatigue(self):
        self._compute_fatigue()
        return self.fatigue 

    def _get_num_clicks(self):
        self._compute_fatigue()
        #Converge to 1 or 2 clicks but in the beginning I am just fuckin hyped to spam click agility markers idek
        clicks = max(2,(randint(1,8) - self.fatigue) // 2) 
        
        return round(clicks)

    def get_fatigued_delay(self, ms):
        """
        return random short delay dependent on fatigue
        """
        #compute fatigue
        self._compute_fatigue()

        #generate delay
        min = ms
        max= ms + 2*math.log(abs(8*ms*self.fatigue))

        print(f"min: {min}, max: {max} fatigue: {self.fatigue}")

        delay = (randint(ms,round(2*ms)) * self.fatigue)/ 1000

        #TODO: Should I Do the delay somewhere outside here..? probably get_delay doesn't seem like you're actually gonna do it...
        time.sleep(delay)
        #time.sleep(ms/1000)

    def chance_to_not_alch(self, base_chance:float):
        """
        chance goes up if we're more tired
        """
        self._compute_fatigue()

        #generate delay
        non_alch = base_chance*(self.fatigue)
        print(f"chance to skip alch {non_alch}")
        return non_alch
    
    def _compute_fatigue(self):

        #additional time
        now = time.time()
        time_since_last_measure = time.time() - self.last_measurement
        self.last_measurement = now

        #fatigue doubles every half hour, make this a cubic I think to model like flowstate and then turbo crash
        self.fatigue += (time_since_last_measure)/1800

        assert self.fatigue >= 1

    def maybe_take_break(self):
        """
        More likely to take a break and for longer the higher fatigue is
        """
        self._compute_fatigue()

        #generate delay
        delay_roll = randint(0,100)

        if delay_roll <= 1 * self.fatigue:
            snooze_time = randint(20,45) * self.fatigue
            time.sleep(snooze_time)

            #Breaks reduce fatigue proportionately to the length
            self.fatigue -= snooze_time/900
        