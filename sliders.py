from kivy.uix.image import Image
from kivy.vector import Vector
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
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
    velocity_x = NumericProperty(2.5)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        if self.pos[0] >= self.lane.puck_area.right - 150:
            self.destroy()
            self.lane.level.lives -= 1
        else:
            self.pos = Vector(*self.velocity) + self.pos

    def destroy(self):
        self.lane.level.empty_beers.remove(self)
        self.lane.puck_area.remove_widget(self)


class BeerPuck(BaseSlider):
    velocity_x = NumericProperty(-5)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        window_cords = self.to_window(*self.pos)

        if window_cords[0] <= 0:
            self.destroy()
            self.lane.level.lives -= 1
        else:
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
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    smack_back = NumericProperty(40)
    smack_timer = NumericProperty(0)
    is_served = BooleanProperty(False)
    smack_velocity_x = NumericProperty(-6)
    forward_velocity_x = NumericProperty(1.5)

    def move(self):
        window_cords = self.to_window(*self.pos)

        if self.pos[0] >= self.lane.puck_area.right - 150:
            self.destroy()
            self.lane.level.lives -= 1
        elif window_cords[0] <= -5:
            self.destroy()
            self.lane.level.score += 10
        elif self.is_served:
            if self.smack_timer <= self.smack_back:
                self.move_along()
            else:
                self.reset_forward_motion()
            self.smack_timer += 1
        else:
            self.move_along()

    def reset_forward_motion(self):
        self.is_served = False
        self.smack_timer = 0
        self.start()
        self.send_beer_back()

    def start(self):
        self.velocity_x = self.forward_velocity_x

    def destroy(self):
        self.lane.level.pucks.remove(self)
        self.lane.puck_area.remove_widget(self)

    def send_beer_back(self):
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
        # TODO:
        # Need a way to make it move back relative to the smack_back
        # And pause/deactivate according to the smack_time

    def move_along(self):
        self.pos = Vector(*self.velocity) + self.pos
