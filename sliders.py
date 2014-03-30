from kivy.uix.image import Image
from kivy.vector import Vector
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
    StringProperty,
)


class BaseSlider(Image):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    lane = ObjectProperty()

    def __init__(self, pos=None, lane=None):
        super(BaseSlider, self).__init__()
        self.size_hint = None, None
        if pos:
            self.pos = pos
        if lane:
            self.lane = lane
        self.start()

    def start(self):
        self.velocity = self.velocity


class EmptyBeer(BaseSlider):
    velocity_x = NumericProperty(3.5)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        if self.collide_widget(self.lane.serve_button):
            self.destroy()
            print('losing life')
            self.lane.level.manager._app.lives -= 1
            return

        self.pos = Vector(*self.velocity) + self.pos

    def destroy(self):
        self.lane.level.empty_beers.remove(self)
        self.lane.puck_area.remove_widget(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.destroy()


class BeerPuck(BaseSlider):
    velocity_x = NumericProperty(-6)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        window_cords = self.to_window(*self.pos)

        if window_cords[0] <= 0:
            self.destroy()
            self.lane.level.manager._app.lives -= 1
            return
        pucks_in_lane = [p for p in self.lane.level.pucks if p.lane == self.lane]
        for puck in pucks_in_lane:
            if puck.collide_widget(self):
                if not puck.is_served:
                    self.collide_handler()
                puck.collide_handler()
                self.lane.level.manager._app.score += 1
                return

        self.pos = Vector(*self.velocity) + self.pos

    def collide_handler(self):
        self.lane.puck_area.remove_widget(self)
        try:
            self.lane.level.beers.remove(self)
        except ValueError:
            pass

    def destroy(self):
        self.lane.level.beers.remove(self)
        self.lane.puck_area.remove_widget(self)


class Puck(BaseSlider):
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
            self.lane.level.manager._app.lives -= 1
        elif window_cords[0] <= -5:
            self.collide()
            self.lane.level.manager._app.score += 10
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

    def destroy(self):
        self.lane.level.pucks.remove(self)
        self.lane.puck_area.remove_widget(self)

    def collide(self):
        self.destroy()
        self.lane.level.total_patrons -= 1

    def send_back(self):
        pos = self.pos
        lane = self.lane
        empty = EmptyBeer(lane=lane)
        empty.pos = pos
        lane.puck_area.add_widget(empty)
        self.lane.level.empty_beers.append(empty)

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

    def halt_movement(self):
        self.velocity_x = 0
