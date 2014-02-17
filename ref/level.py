from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
    BooleanProperty,
    ListProperty,
    StringProperty,
    DictProperty,
)

from patrons.patron import Patron
from main import DropDown, IngrediantDropdownButton


class Level(Screen):

    """
    Level contains everything that every level will have
    """

    hue = NumericProperty(0)
    patrons = ListProperty(())

    def on_pre_enter(self):
        self.patrons = [Patron(level=self) for i in range(self.patron_count - 1)]
        self.setup()

    def on_pre_exit(self):
        self.tear_down()

    def start(self):
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_enter(self):
        self.ready()

    def on_exit(self):
        Clock.unschedule(self.update)

    def ready(self):
        pass

    def setup(self):
        patron = self.patrons.pop()
        self.patron_count -= 1
        self.patron_area.add_widget(patron)
        self.patron_area.on_screen_patrons.append(patron)

        dropdowns = {}
        for main, ingrediants in self.ingrediants.iteritems():
            dropdowns[main] = DropDown()

            for ingrediant in ingrediants:
                btn = Button(text=ingrediant, size_hint_y=None, height=44)
                btn.bind(on_release=lambda btn=btn, dropdown=dropdowns[main]: dropdown.select(btn.text))
                dropdowns[main].add_widget(btn)

            trigger = IngrediantDropdownButton(text=main, size_hint=(None, 1), default_text=main)

            trigger.bind(on_release=dropdowns[main].open)
            dropdowns[main].bind(
                on_select=lambda instance, x, trigger=trigger:
                self.toolbar.dropdown_bar.select_handler(instance, x, trigger)
            )
            self.toolbar.dropdown_bar.add_widget(trigger)
            self.toolbar.dropdown_bar.dropdowns.append(dropdowns[main])

        self.start()
        patron.start()

    def update(self, dt):
        for patron in self.patron_area.on_screen_patrons:
            patron.move()

    def tear_down(self):
        Clock.unschedule(self.update)
