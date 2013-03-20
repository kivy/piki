from random import random
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.properties import *
from kivy.animation import Animation
from kivy.core.window import Window
import RPIO


PIN_P1 = 17
PIN_P2 = 18

RPIO.setup(PIN_P1, RPIO.IN)
RPIO.setup(PIN_P2, RPIO.IN)

PINS = [PIN_P1, PIN_P2]

JUMP_KV = '''

<Player>:
    size: 20,100
    size_hint: None, None
    canvas:
        Color:
            rgb: (1,0,0) if self.state == "down" else (0,0,0)
        PushMatrix
        Translate:
            xy: self.center
        Rotate:
            axis: 0, 0, 1
            angle: self.rotation
        Translate:
            xy: -self.center_x + self.x, -self.center_y + self.y
        Rectangle:
            size: self.size
        PopMatrix

<Hurdle>:
    height: 60
    size_hint: None, None
    canvas:
        Color:
            rgb: 0,0,0
        Rectangle:
            pos: self.pos
            size: self.size

<Jump>:
    player: player
    hurdles: hurdles

    canvas.before:
        Color:
            rgb: self.bg_color
        Rectangle:
            size: self.size

    Widget:
        Label:
            text: "Score: {}".format(player.score)
            font_size: 40
            size: 200,100
            pos: root.width-200, root.height-100

    Widget:
        id: hurdles

    Player:
        id: player
        pos: 200,0



BoxLayout:
    orientation: "vertical"
    Jump:
        player_id: 0
        bg_color: .8,.3,.3
    Jump
        player_id: 1
        bg_color: .3,.3,.8

'''

class Jump(F.RelativeLayout):
    player_id = ObjectProperty(0)
    player = ObjectProperty(None)
    hurdles = ObjectProperty(None)
    speed = NumericProperty(600)
    bg_color = ListProperty([1,1,1])

    def __init__(self, **kwargs):
        self._pin_state = False
        Clock.schedule_interval(self.read_input, 0)
        Clock.schedule_interval(self.update, 1./30.)
        Clock.schedule_interval(self.new_hurdle, 1.)
        super(Jump, self).__init__(**kwargs)

    def read_input(self, *args):
        pin = RPIO.input(PINS[self.player_id])
        if pin and self._pin_state == False:
            self.player.jump()
        self._pin_state = pin

    def update(self, dt):
        for hurdle in self.hurdles.children[:]:
            hurdle.x -= self.speed * dt
            if hurdle.collide_widget(self.player):
                self.player.fall()
            if hurdle.x < -80:
                self.hurdles.remove_widget(hurdle)

    def new_hurdle(self, *args):
        if self.player.state == "down":
            return
        x = self.width + int(random()*200) + 50
        w = 20
        if random() < 0.2:
            w = 40
        self.hurdles.add_widget(Hurdle(x=x, width=w))

class Hurdle(F.Widget):
    pass


class Player(F.Widget):
    jump_anim = ObjectProperty(None)
    state = StringProperty("running")
    score = NumericProperty(0)
    rotation = NumericProperty(0)

    def jump(self):
        if self.state != "running":
            return
        self.state = "jumping"
        self.rotation = 0
        anim = Animation(y=200, t='out_cubic', d=0.2)
        anim += Animation(y=0, t='out_bounce', d=0.3)
        anim2 = Animation(rotation=-360, d=0.4)
        anim = anim & anim2
        anim.bind(on_complete=self.finish_jump)
        self.jump_anim = anim.start(self)

    def finish_jump(self, *args):
        self.state = "running"
        self.score += 1

    def fall(self, *args):
        if self.state == "down":
            return
        if self.state == "jumping" and self.jump_anim:
            self.jump_anim.cancel(self)
        self.state = "down"
        anim = Animation(y=0, rotation=-270, d=0.5)
        anim.start(self)
        Clock.schedule_once(self.get_back_up, 3.0)

    def get_back_up(self, *args):
        self.state = "running"
        anim = Animation(y=0, rotation=0, d=0.5)
        anim.start(self)




class JumpGame(App):
    def build(self):
        return Builder.load_string(JUMP_KV)


JumpGame().run()

