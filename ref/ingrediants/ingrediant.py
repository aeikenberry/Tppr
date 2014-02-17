from random import choice

from kivy.uix.image import Image
from kivy.properties import (
    ObjectProperty,
    StringProperty,
)

POSSIBLE_INGREDIANTS = {
    'milk': ['2%', 'whole', 'almond', 'soy'],
    'coffee': ['espresso', 'coffee', 'decaf coffee', 'cortado', 'latte', 'cappaccino'],
    'sugar': ['sugar', 'raw sugar', 'simple syrup', 'equivia'],
}


class Ingrediant(Image):
    """Ingrediants are what patrons want in the correct order"""
    parent = ObjectProperty(())
    name = StringProperty(())

    def __init__(self, key, *args, **kwargs):
        super(Ingrediant, self).__init__(*args, **kwargs)
