from kivy.app import App
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.vector import Vector
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
    ListProperty,
)


class MainMenu(Screen):
    pass


class BaseSlider(Image):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)


class BeerPuck(BaseSlider):

    def __init__(self, pos=None):
        super(BeerPuck, self).__init__()
        if pos:
            self.pos = pos
        self.start()

    def move(self):
        if self.pos[0] == -500:
            print 'at zero'
        else:
            self.pos = Vector(*self.velocity) + self.pos

    def start(self, vel=(-5, 0)):
        self.velocity = vel


class Puck(BaseSlider):
    pass


class GameState(object):
    pass


class BaseSlider(Image):
    pass


class Lane(GridLayout):
    pass


class Level(Screen):
    lane_one = ObjectProperty()
    lane_two = ObjectProperty()
    lane_three = ObjectProperty()
    lane_four = ObjectProperty()

    beers = ListProperty(())

    def on_pre_enter(self):
        self.setup()
        self.start()

    def update(self, dt):
        for beer in self.beers:
            beer.move()

    def start(self):
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def setup(self):
        pass

    def serve_handler(self, button):
        offset = (300, 0)
        beer = BeerPuck(pos=offset)
        button.lane.puck_area.add_widget(beer)
        self.beers.append(beer)


class Tppr(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu())
        sm.add_widget(Level(name='Level 1'))
        return sm

if __name__ == '__main__':
    Tppr().run()
