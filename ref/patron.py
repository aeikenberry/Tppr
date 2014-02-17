from random import choice
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.vector import Vector
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
    BooleanProperty,
    ListProperty,
    StringProperty,
    DictProperty,
)


class Patron(Image):
    """
    Patron is the base class for the people wanting drinks.
    """
    selected = BooleanProperty(False)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    ingrediants = ListProperty(())

    def __init__(self, level=None, *args, **kwargs):
        super(Patron, self).__init__(*args, **kwargs)
        self.level = level
        self.size_hint = .1, .1
        self.pos = 600, choice([100, 200, 300, 400])
        self.ingrediant_label = []
        # assign ingrediants
        for key, ingrediants in self.level.ingrediants.iteritems():
            self.ingrediants.append(choice(ingrediants))

    def move(self):
        if self.pos[0] == 0:
            self.parent.patron_at_end(self)
        else:
            self.pos = Vector(*self.velocity) + self.pos

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.stop()
            self.show_ingrediants(touch=touch)
            self.level.toolbar.dropdown_bar.active = True
        else:
            self.start()
            self.clear_ingrediants()
            self.level.toolbar.dropdown_bar.reset_dropdowns()

    def show_ingrediants(self, touch=None):
        y = 20
        for ingrediant in self.ingrediants:
            label = Label(text=ingrediant, size=(100, 100), size_hint=(None, None))
            label.pos = (touch.x + 100, touch.y + y)

            layout = FloatLayout(size=(300, 300))
            layout.add_widget(label)
            y += 20
            self.ingrediant_label.append(layout)
            self.level.add_widget(layout)

    def clear_ingrediants(self):
        for layout in self.ingrediant_label:
            print layout
            self.level.remove_widget(layout)

    def on_touch_move(self, touch):
        self.start()

    def start(self, vel=(-4, 0)):
        self.velocity = vel

    def stop(self):
        self.velocity = (0, 0)


class PatronArea(RelativeLayout):
    on_screen_patrons = ListProperty(())

    def patron_at_end(self, patron):
        del self.on_screen_patrons[0]
        self.remove_widget(patron)
        self.level.patron_count -= 1
        self.level.lives -= 1
        if self.level.patrons and self.level.lives:
            self.add_another()
        else:
            self.you_lose()

    def you_win(self):
        label = Label(text='You Win!!')
        self.add_widget(label)
        self.level.tear_down()

    def you_lose(self):
        label = Label(text='You Lost.')
        self.add_widget(label)
        self.level.tear_down()

    def add_another(self):
        patron = self.level.patrons.pop()
        self.add_widget(patron)
        self.on_screen_patrons.append(patron)
        patron.start()
