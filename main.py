from random import choice
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
        else:
            self.pos = Vector(*self.velocity) + self.pos


class Puck(BaseSlider):
    velocity_x = NumericProperty(6)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        if self.pos[0] >= self.lane.puck_area.right - 150:
            self.lane.puck_area.remove_widget(self)
            self.lane.level.pucks.remove(self)
            self.lane.level.lives -= 1
        else:
            self.pos = Vector(*self.velocity) + self.pos


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
    pucks = ListProperty(())
    counter = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super(Level, self).__init__(*args, **kwargs)
        self.lanes = {
            1: self.lane_one,
            2: self.lane_two,
            3: self.lane_three,
            4: self.lane_four,
        }

    def on_pre_enter(self):
        self.setup()
        self.start()

    def update(self, dt):
        for beer in self.beers:
            beer.move()
        if self.lives <= 0:
            self.game_over()
            return
        for puck in self.pucks:
            puck.move()

        if self.counter % 130 == 1:
            lane = self.lanes[choice([1, 2, 3, 4])]
            puck = Puck(lane=lane)
            lane.puck_area.add_widget(puck)
            self.pucks.append(puck)
        self.counter += 1

        for beer in self.beers:
            pucks_in_lane = [p for p in self.pucks if p.lane == beer.lane]
            for puck in pucks_in_lane:
                if beer.collide_widget(puck):
                    beer.lane.puck_area.remove_widget(beer)
                    puck.lane.puck_area.remove_widget(puck)
                    try:
                        self.beers.remove(beer)
                        self.pucks.remove(puck)
                    except ValueError:
                        pass
                    self.score += 1

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
        self.beers.append(beer)
        button.lane.puck_area.add_widget(beer)
        beer.pos = beer.to_local(button_pos[0], 15)


class Tppr(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu())
        sm.add_widget(Level(name='Level 1'))
        return sm

if __name__ == '__main__':
    Tppr().run()
