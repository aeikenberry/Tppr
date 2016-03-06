import random

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

from beer import Beer
from patron import Patron


class Lane(GridLayout):
    patrons = ListProperty()
    beers = ListProperty()
    movers = ReferenceListProperty(patrons, beers)
    serve_button = ObjectProperty()
    counter = NumericProperty(3)
    total_patrons = NumericProperty(0)
    starting_patrons = NumericProperty(0)

    def add_patron(self):
        """
        Add a new patron to the lane, unless it's already full.
        """
        if len(self.patrons) >= self.total_patrons:
            self.counter = 0
            return

        patron = Patron(lane=self)
        patron.pos = patron.pos[0], patron.pos[1] + 15
        self.puck_area.add_widget(patron)
        self.patrons.append(patron)


class Level(Screen):
    lane_one = ObjectProperty()
    lane_two = ObjectProperty()
    lane_three = ObjectProperty()
    lane_four = ObjectProperty()

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

        for i, count in enumerate(kwargs['lane_members'], start=1):
            self.lanes[i].total_patrons = count
            self.lanes[i].starting_patrons = kwargs['starting'][i - 1]

        self.patron_speed = kwargs['patron_speed']
        self.empty_speed = kwargs['empty_speed']
        self.patron_addition_rate = kwargs['respawn_rate']

    def on_pre_enter(self):
        """
        Framework callback to do custom setup
        """
        self.setup()
        self.start()

    def update(self, dt):
        """
        Level 55fps update loop.
        Looks for game over situations
        Moves all things that should move - movables have custom move functions
        Checks to see if the beer closest to the patrons and the patron
        the furthest along are intersection, calling their collision handlers
        """
        if self.manager.get_lives_count() <= 0:
            return self.game_over()

        if not any([patron for lane in self.lanes.values() for patron in lane.patrons]):
            return self.you_won()

        for lane in self.lanes.values():
            for group in lane.movers:
                for mover in group:
                    if mover._move:
                        mover.move()

            beers = sorted([beer for beer in lane.beers if not beer.empty], key=lambda x: x.pos[0])
            patrons = sorted(lane.patrons, key=lambda x: x.pos[0], reverse=True)

            try:
                beer = beers[0]
                patron = patrons[0]
                if beer.collide_widget(patron) and patron._move:
                    beer.collide_handler()
                    patron.collide_handler()
            except IndexError:
                pass

            if lane.counter % self.patron_addition_rate + random.randrange(0, 12) == 1:
                lane.add_patron()

            lane.counter += 1

    def start(self):
        """
        Schedules update loop.
        """
        Clock.schedule_interval(self.update, 1.0 / 55.0)

    def game_over(self):
        """
        Game Over encapsulates end-of-level-loss
        """
        self.end_of_level()
        self.message_holder.add_widget(self.you_lose_label)
        Clock.schedule_once(self.goto_menu, 5)

    def goto_menu(self, *args):
        """
        Reset state and return to main menu.
        """
        self.manager.current = 'Main Menu'
        self.reset()
        self.manager.reset()

    def you_won(self):
        """
        This level is complete and you progress to
        the next level.
        """
        self.end_of_level()
        self.message_holder.add_widget(self.you_win_label)
        Clock.schedule_once(self.goto_next_level, 5)

    def goto_next_level(self, *args):
        """
        Use the ScreenManager to go to the next level and
        clear out the current level.
        """
        self.manager.current = self.manager.next()
        self.reset()

    def end_of_level(self):
        """
        Make sure update loop ends and touchable
        get cancelled.
        """
        Clock.unschedule(self.update)
        self.no_events()

    def no_events(self):
        """
        Cancel touch events for all lanes
        """
        for lane in self.lanes.values():
            lane.disabled = True
            for empty in lane.beers:
                empty.touchable = False

    def reset(self):
        """
        Resets the state for lanes and labels
        """
        for lane in self.lanes.values():
            lane.puck_area.clear_widgets()
            lane.patrons = list()
            lane.disabled = False
            lane.beers = list()

        self.message_holder.remove_widget(self.you_lose_label)
        self.message_holder.remove_widget(self.you_win_label)

    def setup(self):
        """
        Adds the starting patrons to the lanes.
        """
        for lane in self.lanes.values():
            for p in range(lane.starting_patrons):
                patron = Patron(lane=lane)
                patron.pos = patron.pos[0], patron.pos[1] + 15
                lane.puck_area.add_widget(patron)
                lane.patrons.append(patron)

    def serve_handler(self, button):
        """
        Callback when serve button was pressed.
        """
        button_pos = list(button.to_window(*button.pos))
        button_pos[0] -= 100
        beer = Beer(lane=button.lane)
        button.lane.puck_area.add_widget(beer)
        button.lane.beers.append(beer)
        beer.pos = beer.to_local(button_pos[0], 15)
