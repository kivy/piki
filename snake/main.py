from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.vector import Vector
import RPIO

PIN_P1 = 17
PIN_P2 = 18

RPIO.setup(PIN_P1, RPIO.IN)
RPIO.setup(PIN_P2, RPIO.IN)

Builder.load_string('''
<Run>:
    canvas.before:
        Color:
            hsv: .8, 1, .5
        Rectangle:
            size: self.size

<Player>:
        Color:
            hsv: .2, 1, 1
        Line:
            points: root.line
        Ellipse:
            size: root.circle * 2, root.circle * 2
            pos: root.pos[0] - root.circle, root.pos[1] - root.circle

''')


class Player(Widget):
    dir = NumericProperty(0)
    line = ListProperty([])
    circle = NumericProperty(12)

    def update(self, dt, press):
        sensitivity = 500. * dt
        speed = 300. * dt

        self.dir += sensitivity if press else -sensitivity

        v = Vector(speed, 0).rotate(self.dir)
        x, y = Vector(*self.pos) + v
        x %= self.width
        y %= self.height
        self.pos = x, y
        self.line = (self.p1_line + [x, y])[-100:]

class Run(FloatLayout):
    p2_dir = NumericProperty(0)
    p1_pos = ListProperty([300, 500])
    p2_pos = ListProperty([300, 500])
    p2_line = ListProperty([])

    def __init__(self, **kwargs):
       super(Run, self).__init__(**kwargs) 
       Clock.schedule_interval(self.read_gpio, 0)
       self.player1 = Player()
       self.add_widget(self.player1)
       self.player2 = Player()
       self.add_widget(self.player2)

    def read_gpio(self, dt):
        p1 = RPIO.input(PIN_P1)
        p2 = RPIO.input(PIN_P2)

        self.player1.update(dt, p1)
        self.player2.update(dt, p2)




class RunGame(App):
    def build(self):
        return Run()

RunGame().run()

