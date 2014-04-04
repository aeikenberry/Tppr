from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
    StringProperty,
)


class BaseSlider(Image):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    lane = ObjectProperty()
    _move = BooleanProperty(True)

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

    def fade_out(self, d=1, *args):
        anim = Animation(opacity=0, duration=d)
        anim.start(self)
        Clock.schedule_once(self.destroy, .5)

    def make_red(self):
        self.source = 'img/red.png'
        self.reload()

    def halt_movement(self):
        self.velocity_x = 0


class EmptyBeer(BaseSlider):
    velocity_x = NumericProperty(3.5)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, *args, **kwargs):
        super(EmptyBeer, self).__init__(*args, **kwargs)
        self.touchable = True
        anim = Animation(opacity=.7) + Animation(opacity=1)
        anim.repeat = True
        anim.start(self)

    def move(self):
        if self.pos[0] >= self.lane.serve_button.pos[0] - self.lane.serve_button.width:
            self.collide_handler()
            self.lane.level.manager._app.lives -= 1

        self.pos = Vector(*self.velocity) + self.pos

    def collide_handler(self):
        self._move = False
        self.fade_out()

    def destroy(self, *args):
        try:
            self.lane.level.empty_beers.remove(self)
            self.lane.puck_area.remove_widget(self)
            self = None
        except ValueError:
            pass

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.touchable:
            self.destroy()


class BeerPuck(BaseSlider):
    velocity_x = NumericProperty(-7.5)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        window_cords = self.to_window(*self.pos)

        if window_cords[0] <= 0:
            return self.hit_wall()

        for puck in self.lane.pucks:
            if puck.collide_widget(self):
                if not puck.is_served:
                    self.collide_handler()
                puck.collide_handler()
                self.lane.level.manager._app.score += 1
                return

        self.pos = Vector(*self.velocity) + self.pos

    def collide_handler(self):
        self._move = False
        self.fade_out(d=.2)

    def hit_wall(self):
        self._move = False
        self.lane.level.manager._app.lives -= 1
        self.start_remove()

    def start_remove(self):
        self.make_red()
        Clock.schedule_once(self.fade_out, .5)

    def destroy(self, *args):
        try:
            self.lane.level.beers.remove(self)
            self.lane.puck_area.remove_widget(self)
            self.lane.beers.remove(self)
            self = None
        except ValueError:
            pass


class Puck(BaseSlider):
    # Current Velocity
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    # Properties for when beer collision smack-back
    smack_back_duration = NumericProperty(30)
    smack_timer = NumericProperty(0)
    is_served = BooleanProperty(False)
    smack_velocity_x = NumericProperty(-7.5)

    # Normal State
    forward_velocity_x = NumericProperty(3)

    # Patrons move forward and then pause
    forward_delay_duration = NumericProperty(90)
    forward_delay_interval = NumericProperty(50)
    forward_delay_timer = NumericProperty(0)
    is_delayed = BooleanProperty(False)
    state = StringProperty()

    class State(object):
        """
        Puck.State.FORWARD
        """
        FORWARD = 'forward'
        BACKWARDS = 'backwards'
        STOPPED = 'stopped'

    def move(self):
        window_cords = self.to_window(*self.pos)

        #if self.pos[0] >= self.lane.serve_button.pos[0] - self.lane.serve_button.width:
        if self.collide_widget(self.lane.serve_button):
            self.collide()
            self.lane.level.manager._app.lives -= 1
        elif window_cords[0] <= -5:
            self.collide()
            self.lane.level.manager._app.score += 10
        elif self.is_served:
            if self.smack_timer <= self.smack_back_duration:
                self.move_along()
            else:
                self.reset_forward_motion()
            self.smack_timer += 1
        else:
            self.move_along()

    def reset_forward_motion(self):
        self.is_served = False
        self.smack_timer = 0
        self.forward_delay_timer = 0
        self.start()
        self.send_back()

    def start(self):
        self.velocity_x = self.forward_velocity_x

    def destroy(self, *args):
        self.lane.level.pucks.remove(self)
        self.lane.puck_area.remove_widget(self)
        self.lane.pucks.remove(self)
        self = None

    def collide(self):
        self._move = False
        self.fade_out(d=.3)
        self.lane.level.total_patrons -= 1

    def send_back(self):
        pos = self.pos
        lane = self.lane
        empty = EmptyBeer(lane=lane)
        empty.pos = pos
        lane.puck_area.add_widget(empty)
        self.lane.level.empty_beers.append(empty)
        self.lane.beers.append(empty)

    def collide_handler(self):
        if not self.is_served:
            self.is_served = True
            self.velocity_x = self.smack_velocity_x
            self.forward_delay_timer = 0

    def continue_moving(self):
        self.pos = Vector(*self.velocity) + self.pos

    def move_along(self):
        if self.forward_delay_timer <= self.forward_delay_interval:
            self.continue_moving()
        elif self.forward_delay_timer <= self.forward_delay_duration:
            pass
        else:
            self.forward_delay_timer = 0
        self.forward_delay_timer += 1
