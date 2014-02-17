from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.properties import (
    NumericProperty,
    BooleanProperty,
    ListProperty,
    StringProperty,
    DictProperty,
)

from levels.level import Level


class MainMenu(Screen):
    hue = NumericProperty(0)


class Toolbar(GridLayout):
    pass


class IngrediantDropdownButton(Button):
    default_text = StringProperty()


class DropdownBar(GridLayout):
    active = BooleanProperty(False)
    ingrediants = ListProperty(())
    dropdowns = ListProperty(())

    def select_handler(self, instance, x, trigger):
        if self.active:
            setattr(trigger, 'text', x)

    def reset_dropdowns(self):
        for btn in self.children:
            btn.text = btn.default_text


class Level1(Level):
    patron_count = NumericProperty(10)
    level_number = StringProperty('1')
    lives = NumericProperty(5)
    level_title = StringProperty('Baby Steps')
    ingrediant_count = NumericProperty(3)
    ingrediants = DictProperty({
        'Milks': ['Whole Milk', 'Soy', 'Creamer'],
        'Coffees': ['Drip Coffee', 'Espresso', 'Pour Over'],
        'Sugars': ['Sugar', 'Simple Syrup', 'Raw Sugar'],
    })


class Ingrediant(Image):
    name = StringProperty('')


class Player(Widget):
    pass


class CallOfDuty(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu())
        sm.add_widget(Level1(name='Level 1'))
        return sm


if __name__ == '__main__':
    CallOfDuty().run()
