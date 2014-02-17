from kivy.app import App
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
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


class BeerPuck(BaseSlider):
    velocity_x = NumericProperty(-5)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        window_cords = self.to_window(*self.pos)

        if window_cords[0] <= 0:
            self.lane.level.beers.remove(self)
            self.lane.level.lives -= 1
            self.lane.puck_area.remove_widget(self)

            pass
        else:
            # print 'pos:', self.pos
            # print 'window_pos:', window_cords
            # print 'size:', self.size
            self.pos = Vector(*self.velocity) + self.pos


class Puck(BaseSlider):
    velocity_x = NumericProperty(6)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)


class GameState(object):
    lives = NumericProperty(3)
    score = NumericProperty(0)


class Lane(GridLayout):
    pass


class Level(Screen):
    lane_one = ObjectProperty()
    lane_two = ObjectProperty()
    lane_three = ObjectProperty()
    lane_four = ObjectProperty()
    score = NumericProperty(0)
    lives = NumericProperty(3)
    beers = ListProperty(())

    def on_pre_enter(self):
        self.setup()
        self.start()

    def update(self, dt):
        for beer in self.beers:
            beer.move()
        if self.lives <= 0:
            self.game_over()

    def start(self):
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def game_over(self):
        Clock.unschedule(self.update)
        label = Label(text='You Lost.')
        self.lane_one.add_widget(label)

    def setup(self):
        pass

    def serve_handler(self, button):
        button_pos = list(button.to_window(*button.pos))
        button_pos[0] -= 100
        beer = BeerPuck(lane=button.lane)
        button.lane.puck_area.add_widget(beer)
        beer.pos = beer.to_local(button_pos[0], 15)
        self.beers.append(beer)


class Tppr(App):

    def build(self):
        state = GameState()
        sm = ScreenManager()
        sm.state = state
        sm.add_widget(MainMenu())
        sm.add_widget(Level(name='Level 1'))
        return sm

if __name__ == '__main__':
    Tppr().run()
