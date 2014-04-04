import gc
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy.properties import NumericProperty
from level import Level
from levels import LEVELS

__version__ = '0.2.01'


class MainMenu(Screen):
    pass


class TpprMngr(ScreenManager):

    def __init__(self, *args, **kwargs):
        super(ScreenManager, self).__init__(*args, **kwargs)
        self._app = kwargs['app']
        self._load_screens()
        Clock.schedule_interval(self.collect_garbage, 30)
        sound = SoundLoader.load('audio/background1.ogg')
        if sound:
            sound.loop = True
            sound.play()

    def collect_garbage(self, *args):
        gc.collect()

    def load_levels(self):
        """
        Parses the level specs from levels.py
        """
        for i, level in enumerate(LEVELS, start=1):
            if not 'name' in level:
                level['name'] = "Level {}".format(i)
            self.add_widget(Level(**level))

    def _load_screens(self):
        """
        Loads all the screens for the game.
        """
        self.add_menu()
        self.load_levels()

    def add_menu(self):
        """
        Adds the main menu.
        """
        self.add_widget(self.get_menu())

    def get_menu(self):
        """
        Returns the Screen that will be the Main Menu
        """
        return MainMenu(name='Main Menu')


class Tppr(App):
    score = NumericProperty(0)
    lives = NumericProperty(3)

    def reset(self):
        self.score = 0
        self.lives = 3

    def build(self):
        return TpprMngr(transition=RiseInTransition(), app=self)

if __name__ == '__main__':
    Tppr().run()
