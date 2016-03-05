import gc

from kivy.clock import Clock
from kivy.vector import Vector
from kivy.properties import (
    NumericProperty,
    ReferenceListProperty,
)

from sliders import BaseSlider


class Beer(BaseSlider):
    empty = False

    velocity_x = NumericProperty(-7.5)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        window_cords = self.to_window(*self.pos)

        if window_cords[0] <= 0:
            return self.hit_wall()

        self.pos = Vector(*self.velocity) + self.pos

    def collide_handler(self):
        self._move = False
        self.fade_out(d=.2)

    def hit_wall(self):
        print "hit wall"
        self._move = False
        self.lane.level.manager.lost_life()
        self.start_remove()

    def start_remove(self):
        self.make_red()
        Clock.schedule_once(self.fade_out, .5)

    def destroy(self, *args):
        try:
            self.lane.puck_area.remove_widget(self)
            self.lane.beers.remove(self)
            del self
        except ValueError:
            pass
        gc.collect()
