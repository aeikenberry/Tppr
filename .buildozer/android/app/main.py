from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty
from level import Level


class MainMenu(Screen):
    pass


class TpprMngr(ScreenManager):

    def __init__(self, *args, **kwargs):
        super(ScreenManager, self).__init__(*args, **kwargs)
        self._app = kwargs['app']


class Tppr(App):
    score = NumericProperty(0)
    lives = NumericProperty(3)

    def reset(self):
        self.score = 0
        self.lives = 3

    def build(self):
        sm = TpprMngr(app=self)
        sm.add_widget(MainMenu(name='Main Menu'))
        sm.add_widget(Level(name='Level 1', patrons=10, starting=1))
        sm.add_widget(Level(name='Level 2', patrons=15, starting=2))
        sm.add_widget(Level(name='Level 3', patrons=20, starting=4))
        return sm

if __name__ == '__main__':
    Tppr().run()

__version__ = '0.1.2'
