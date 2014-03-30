import time
from random import choice
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
    ListProperty,
)

from sliders import Puck, BeerPuck


class Lane(GridLayout):
    pass


class Level(Screen):
    lane_one = ObjectProperty()
    lane_two = ObjectProperty()
    lane_three = ObjectProperty()
    lane_four = ObjectProperty()
    beers = ListProperty(())
    empty_beers = ListProperty(())
    pucks = ListProperty(())
    movers = ReferenceListProperty(beers, pucks, empty_beers)
    counter = NumericProperty(0)
    puck_addition_rate = NumericProperty(113)

    def __init__(self, *args, **kwargs):
        super(Level, self).__init__(*args, **kwargs)
        self.lanes = {
            1: self.lane_one,
            2: self.lane_two,
            3: self.lane_three,
            4: self.lane_four,
        }
        self.you_lose_label = Label(text='You Lost.')
        self.you_win_label = Label(text='Level Complete!')
        self.total_patrons = kwargs['patrons']
        self._total_patrons = kwargs['patrons']
        self.starting_patrons = kwargs['starting']

    def on_pre_enter(self):
        self.setup()
        self.start()

    def update(self, dt):
        if self.manager._app.lives <= 0:
            self.game_over()
            return

        for group in self.movers:
            for obj in group:
                obj.move()

        if self.counter % self.puck_addition_rate == 1 and self.total_patrons > 0:
            self.add_puck()
        self.counter += 1

        for beer in self.beers:
            pucks_in_lane = [p for p in self.pucks if p.lane == beer.lane]
            for puck in pucks_in_lane:
                if beer.collide_widget(puck):
                    if not puck.is_served:
                        beer.collide_handler()
                    puck.collide_handler()
                    self.manager._app.score += 1

    def start(self):
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        for i in range(self.starting_patrons - 1):
            self.add_puck()

    def add_puck(self):
        lane = self.lanes[choice([1, 2, 3, 4])]
        puck = Puck(lane=lane)
        puck.pos = puck.pos[0], puck.pos[1] + 15
        lane.puck_area.add_widget(puck)
        self.pucks.append(puck)
        self.total_patrons -= 1

    def game_over(self):
        self.add_widget(self.you_lose_label)
        Clock.unschedule(self.update)
        time.sleep(4)
        self.manager.current = 'Main Menu'
        self.reset()
        self.manager._app.reset()

    def you_won(self):
        self.add_widget(self.you_win_label)
        Clock.unschedule(self.update)
        time.sleep(4)
        self.manager.current = self.manager.next()
        self.reset()

    def reset(self):
        self.beers = list()
        self.pucks = list()
        for num, lane in self.lanes.items():
            lane.puck_area.clear_widgets()
        self.remove_widget(self.you_lose_label)
        self.remove_widget(self.you_win_label)
        self.total_patrons = self._total_patrons

    def setup(self):
        pass

    def serve_handler(self, button):
        button_pos = list(button.to_window(*button.pos))
        button_pos[0] -= 100
        beer = BeerPuck(lane=button.lane)
        self.beers.append(beer)
        button.lane.puck_area.add_widget(beer)
        beer.pos = beer.to_local(button_pos[0], 15)
