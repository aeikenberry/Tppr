import gc
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.clock import Clock
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
    _move = BooleanProperty(True)

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

    def fade_out(self, d=1, *args):
        anim = Animation(opacity=0, duration=d)
        anim.start(self)
        Clock.schedule_once(self.destroy, .5)

    def make_red(self):
        self.source = 'img/red.png'
        self.reload()

    def halt_movement(self):
        self.velocity_x = 0


class EmptyBeer(BaseSlider):
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

    def destroy(self, *args):
        try:
            self.lane.puck_area.remove_widget(self)
            del(self)
        except ValueError:
            pass
        gc.collect()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.touchable:
            self.destroy()


class BeerPuck(BaseSlider):
    pass


class Puck(BaseSlider):
    pass
