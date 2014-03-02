import time
from random import choice
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.vector import Vector
from kivy.properties import (
    BooleanProperty,
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

    def collide_handler(self):
        self.lane.puck_area.remove_widget(self)
        try:
            self.lane.level.beers.remove(self)
        except ValueError:
            pass


class Beer(Button):
    pass


class Puck(BaseSlider):
    velocity_x = NumericProperty(2.5)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    smack_back = NumericProperty(40)
    smack_timer = NumericProperty(0)
    is_served = BooleanProperty(False)
    smack_velocity_x = NumericProperty(-6)
    forward_velocity_x = NumericProperty(2.5)

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
                self.is_served = False
                self.smack_timer = 0
                self.velocity_x = self.forward_velocity_x
            self.smack_timer += 1
        else:
            'moving along'
            self.move_along()

    def destroy(self):
        self.lane.level.pucks.remove(self)
        self.lane.puck_area.remove_widget(self)

    def collide_handler(self):
        if not self.is_served:
            self.is_served = True
            self.velocity_x = self.smack_velocity_x
        # Need a way to make it move back relative to the smack_back
        # And pause/deactivate according to the smack_time

    def move_along(self):
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
        self.you_lose_label = Label(text='You Lost.')

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
            puck.pos = puck.pos[0], puck.pos[1] + 15
            lane.puck_area.add_widget(puck)
            self.pucks.append(puck)
        self.counter += 1

        for beer in self.beers:
            pucks_in_lane = [p for p in self.pucks if p.lane == beer.lane]
            for puck in pucks_in_lane:
                if beer.collide_widget(puck):
                    if not puck.is_served:
                        beer.collide_handler()
                    puck.collide_handler()
                    self.score += 1

    def start(self):
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def game_over(self):
        Clock.unschedule(self.update)
        self.lane_one.add_widget(self.you_lose_label)
        time.sleep(4)
        self.manager.current = self.manager.previous()
        self.reset()

    def reset(self):
        self.beers = list()
        self.pucks = list()
        for num, lane in self.lanes.items():
            lane.puck_area.clear_widgets()
        self.score = 0
        self.lives = 3
        self.lane_one.remove_widget(self.you_lose_label)

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
