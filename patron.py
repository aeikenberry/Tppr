import gc

from kivy.vector import Vector
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    StringProperty,
)

from beer import EmptyBeer
from sliders import BaseSlider


class Patron(BaseSlider):
    is_served = BooleanProperty(False)

    # how fast they get smacked back and how long
    smack_velocity_x = NumericProperty(-8.5)
    smack_back_duration = NumericProperty(60)
    smack_timer = NumericProperty(0)

    # how long they should chill before moving again
    stop_duration = NumericProperty(75)
    stop_timer = NumericProperty(0)

    # Normal State
    forward_velocity_x = NumericProperty(3)

    # Patrons move forward and then pause
    forward_delay_duration = NumericProperty(120)
    forward_delay_interval = NumericProperty(50)
    forward_delay_timer = NumericProperty(0)

    state = StringProperty()

    def __init__(self, *args, **kwargs):
        lane_speed = kwargs.pop('lane_speed')
        pause_duration = kwargs.pop('pause_duration')
        self.forward_velocity_x = lane_speed
        self.forward_delay_duration = pause_duration
        super(Patron, self).__init__(*args, **kwargs)

    class MovementState(object):
        """
        Puck.State.FORWARD
        """
        FORWARD = 'forward'
        BACKWARDS = 'backwards'
        PAUSED = 'paused'
        DRINKING = 'drinking'

    @property
    def movable(self):
        return self._move

    @property
    def can_collide(self):
        return self.state in [self.MovementState.PAUSED, self.MovementState.FORWARD]

    def move(self):
        window_cords = self.to_window(*self.pos)

        if self.collide_widget(self.lane.serve_button):
            # This patron made it to the end of the bar :(
            self.collide()
            self.lane.level.manager.lost_life()
            return

        if window_cords[0] <= -5:
            # Patron has slid out of the bar
            self.collide()
            self.lane.level.manager.add_to_score(10)
            return

        if self.is_served:
            self.served_state_move_handler()
            return

        # Default state : Moving forward (with pauses)
        self.forward_motion_handler()

    # Update cycle motion handlers

    def served_state_move_handler(self):
        if self.state == self.MovementState.BACKWARDS:
            # Patron is being knocked back

            if self.smack_timer <= self.smack_back_duration:
                # Continue to move backwards

                self.smack_timer += 1
                self.continue_motion_in_current_dir()
            else:
                self.smack_timer = 0
                self.drink()

        if self.state == self.MovementState.DRINKING:
            # Patron has been knocked back but not out. chills for a bit.

            if self.stop_timer <= self.stop_duration:
                # stay stopped
                self.stop_timer += 1
            else:
                # start again, send you beer back down
                self.stop_timer = 0
                self.reset_forward_motion()

    def forward_motion_handler(self):
        if self.state == self.MovementState.FORWARD:
            # Currently Moving Forward

            if self.forward_delay_timer <= self.forward_delay_interval:
                # Keep on
                self.continue_motion_in_current_dir()
                self.forward_delay_timer += 1
            else:
                self.stop()
                self.forward_delay_timer = 0

        if self.state == self.MovementState.PAUSED:
            # Moving forward, but paused

            if self.forward_delay_timer <= self.forward_delay_duration:
                # Keep on
                self.continue_motion_in_current_dir()
                self.forward_delay_timer += 1
            else:
                self.forward()
                self.forward_delay_timer = 0

    def continue_motion_in_current_dir(self):
        self.pos = Vector(*self.velocity) + self.pos

    def reset_forward_motion(self):
        self.is_served = False
        self.forward()

    # Movement Handlers

    def start(self):
        self.forward()

    def forward(self):
        self.velocity_x = self.forward_velocity_x
        self.state = self.MovementState.FORWARD

    def stop(self):
        self.velocity_x = 0
        self.state = self.MovementState.PAUSED

    def drink(self):
        self.velocity_x = 0
        self.state = self.MovementState.DRINKING
        self.send_back()

    def backwards(self):
        self.velocity_x = self.smack_velocity_x
        self.state = self.MovementState.BACKWARDS

    # Destroy

    def destroy(self, *args):
        self.lane.puck_area.remove_widget(self)
        self.lane.patrons.remove(self)
        del self
        gc.collect()

    def collide(self):
        self._move = False
        self.fade_out(d=.3)

    def send_back(self):
        empty = EmptyBeer(lane=self.lane)
        empty.pos = self.pos

        self.lane.puck_area.add_widget(empty)
        self.lane.beers.append(empty)

    def collide_handler(self):
        if not self.is_served:
            self.is_served = True
            self.velocity_x = self.smack_velocity_x
            self.state = self.MovementState.BACKWARDS
            self.forward_delay_timer = 0

    def continue_moving(self):
        self.pos = Vector(*self.velocity) + self.pos
