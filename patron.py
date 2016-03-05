import gc

from kivy.vector import Vector
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ReferenceListProperty,
    StringProperty,
)

from sliders import BaseSlider, EmptyBeer


class Patron(BaseSlider):
    # Current Velocity
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    # Properties for when beer collision smack-back
    smack_back_duration = NumericProperty(30)
    smack_timer = NumericProperty(0)
    is_served = BooleanProperty(False)
    smack_velocity_x = NumericProperty(-7.5)

    # Normal State
    forward_velocity_x = NumericProperty(3)

    # Patrons move forward and then pause
    forward_delay_duration = NumericProperty(90)
    forward_delay_interval = NumericProperty(50)
    forward_delay_timer = NumericProperty(0)
    is_delayed = BooleanProperty(False)
    state = StringProperty()

    class State(object):
        """
        Puck.State.FORWARD
        """
        FORWARD = 'forward'
        BACKWARDS = 'backwards'
        STOPPED = 'stopped'

    def move(self):
        window_cords = self.to_window(*self.pos)

        if self.collide_widget(self.lane.serve_button):
            self.collide()
            self.lane.level.manager.lost_life()
        elif window_cords[0] <= -5:
            self.collide()
            self.lane.level.manager.add_to_score(10)
        elif self.is_served:
            if self.smack_timer <= self.smack_back_duration:
                self.move_along()
            else:
                self.reset_forward_motion()
            self.smack_timer += 1
        else:
            self.move_along()

    def reset_forward_motion(self):
        self.is_served = False
        self.smack_timer = 0
        self.forward_delay_timer = 0
        self.start()
        self.send_back()

    def start(self):
        self.velocity_x = self.forward_velocity_x

    def destroy(self, *args):
        self.lane.puck_area.remove_widget(self)
        self.lane.patrons.remove(self)
        del self
        gc.collect()

    def collide(self):
        self._move = False
        self.fade_out(d=.3)

    def send_back(self):
        pos = self.pos
        lane = self.lane
        empty = EmptyBeer(lane=lane)
        empty.pos = pos
        lane.puck_area.add_widget(empty)

    def collide_handler(self):
        if not self.is_served:
            self.is_served = True
            self.velocity_x = self.smack_velocity_x
            self.forward_delay_timer = 0

    def continue_moving(self):
        self.pos = Vector(*self.velocity) + self.pos

    def move_along(self):
        if self.forward_delay_timer <= self.forward_delay_interval:
            self.continue_moving()
        elif self.forward_delay_timer <= self.forward_delay_duration:
            pass
        else:
            self.forward_delay_timer = 0
        self.forward_delay_timer += 1
