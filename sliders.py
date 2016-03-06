from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.clock import Clock
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
