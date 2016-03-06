import gc

from kivy.animation import Animation
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


class EmptyBeer(Beer):
    empty = True
    velocity_x = NumericProperty(3.5)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, *args, **kwargs):
        super(EmptyBeer, self).__init__(*args, **kwargs)
        self.touchable = True
        anim = Animation(opacity=.7) + Animation(opacity=1)
        anim.repeat = True
        anim.start(self)

    def move(self):
        if self.pos[0] >= self.lane.serve_button.pos[0] - self.lane.serve_button.width:
            self.collide_handler()
            self.lane.level.manager.lost_life()

        self.pos = Vector(*self.velocity) + self.pos

    def collide_handler(self):
        self._move = False
        self.fade_out()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.touchable:
            self.destroy()
