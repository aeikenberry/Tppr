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
    pucks = ListProperty(())
    beers = ListProperty(())
    serve_button = ObjectProperty()


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
    message_delay_time = NumericProperty(30)
    message_holder = ObjectProperty()

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
        self.patrons = kwargs['starting']

        self.puck_speed = kwargs['puck_speed']
        self.empty_speed = kwargs['empty_speed']
        self.puck_addition_rate = kwargs['spawn_rate']

    def on_pre_enter(self):
        self.setup()
        self.start()

    def update(self, dt):
        if self.manager._app.lives <= 0:
            return self.game_over()

        if self.total_patrons <= 0:
            return self.you_won()

        for group in self.movers:
            for obj in group:
                if obj._move:
                    obj.move()

        for lane in self.lanes.values():
            lane.beers = sorted(lane.beers, key=lambda x: x.pos[0])
            lane.pucks = sorted(lane.pucks, key=lambda x: x.pos[0], reverse=True)
            try:
                beer = lane.beers[0]
                puck = lane.pucks[0]
                if beer.collide_widget(puck) and puck._move:
                    beer.collide_handler()
                    puck.collide_handler()
            except IndexError:
                pass

        if self.counter % self.puck_addition_rate == 1 and self.total_patrons > 0:
            self.add_puck()

        self.counter += 1

    def start(self):
        Clock.schedule_interval(self.update, 1.0 / 55.0)

    def add_puck(self):
        lane = self.lanes[choice([1, 2, 3, 4])]
        puck = Puck(lane=lane)
        puck.pos = puck.pos[0], puck.pos[1] + 15
        lane.puck_area.add_widget(puck)
        self.pucks.append(puck)
        lane.pucks.append(puck)

    def game_over(self):
        self.end_of_level()
        self.message_holder.add_widget(self.you_lose_label)
        Clock.schedule_once(self.goto_menu, 5)

    def goto_menu(self, *args):
        self.manager.current = 'Main Menu'
        self.reset()
        self.manager._app.reset()

    def you_won(self):
        self.end_of_level()
        self.message_holder.add_widget(self.you_win_label)
        Clock.schedule_once(self.goto_next_level, 5)

    def goto_next_level(self, *args):
        self.manager.current = self.manager.next()
        self.reset()

    def end_of_level(self):
        Clock.unschedule(self.update)
        self.no_events()

    def no_events(self):
        for lane in self.lanes.values():
            lane.disabled = True
            for empty in lane.beers:
                empty.touchable = False

    def reset(self):
        for beer in self.beers:
            beer.destroy()
        self.beers = list()
        for puck in self.pucks:
            puck.destroy()
        self.pucks = list()
        for empty in self.empty_beers:
            empty.destroy()
        self.empty_beers = list()
        for lane in self.lanes.values():
            lane.puck_area.clear_widgets()
            lane.pucks = list()
            lane.disabled = False
            lane.beers = list()

        self.message_holder.remove_widget(self.you_lose_label)
        self.message_holder.remove_widget(self.you_win_label)
        self.total_patrons = self._total_patrons

    def setup(self):
        # create the starting pucks
        for i, starting in enumerate(self.patrons):
          lane = self.lanes[i+1]
          for p in range(starting):
            puck = Puck(lane=lane)
            puck.pos = puck.pos[0], puck.pos[1] + 15
            lane.puck_area.add_widget(puck)
            self.pucks.append(puck)
            lane.pucks.append(puck)

    def serve_handler(self, button):
        button_pos = list(button.to_window(*button.pos))
        button_pos[0] -= 100
        beer = BeerPuck(lane=button.lane)
        self.beers.append(beer)
        button.lane.puck_area.add_widget(beer)
        button.lane.beers.append(beer)
        beer.pos = beer.to_local(button_pos[0], 15)
