from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.lang import Builder
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

        Color:
            hsv: .2, 1, 1
        Rectangle:
            size: self.width * root.p1 / float(self.score), 100.
            pos: 0, root.center_y - 200

        Color:
            hsv: .5, 1, 1
        Rectangle:
            size: self.width * root.p2 / float(self.score), 100.
            pos: 0, root.center_y + 100

    Label:
        text: root.win_text + '\\n' +  (str(int(root.ready_timer)) if int(root.ready_timer) > 0 else '')
        font_size: 80
''')


class Run(FloatLayout):
    win_text = StringProperty('')
    ready_timer = NumericProperty(10.)
    p1 = NumericProperty(0)
    p2 = NumericProperty(0)
    p1_state = NumericProperty(0)
    p2_state = NumericProperty(0)
    score = NumericProperty(30)

    def __init__(self, **kwargs):
       super(Run, self).__init__(**kwargs) 
       Clock.schedule_interval(self.read_gpio, 0)

    def read_gpio(self, dt):
        self.ready_timer -= dt
        if int(self.ready_timer) > 0:
            return

        self.win_text = ''
        p1 = RPIO.input(PIN_P1)
        p2 = RPIO.input(PIN_P2)

        if p1 and self.p1_state == 0:
            self.p1_state = 1
            self.p1 += 1
        elif not p1 and self.p1_state == 1:
            self.p1_state = 0

        if p2 and self.p2_state == 0:
            self.p2_state = 1
            self.p2 += 1
        elif not p2 and self.p2_state == 1:
            self.p2_state = 0
            
        if self.p1 >= self.score:
            self.win_text = 'Player 1 win !'
            self.ready_timer = 5.
            self.p1 = self.p2 = 0
        elif self.p2 >= self.score:
            self.win_text = 'Player 2 win !'
            self.ready_timer = 5.
            self.p1 = self.p2 = 0

class RunGame(App):
    def build(self):
        return Run()

RunGame().run()

