from random import randint, random
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
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
            hsv: .8, .5, .2, 
        Rectangle:
            size: self.size

<Player>:
    canvas:
        Color:
            hsv: root.color, 1, 1
        Line:
            points: root.line
        Ellipse:
            size: root.radius * 2, root.radius * 2
            pos: root.pos[0] - root.radius, root.pos[1] - root.radius
        Color:
            rgba: 1, 1, 1, .5
        PushMatrix
        Translate:
            xy: root.pos
        Rotate:
            axis: 0, 0, 1
            angle: root.dir - 90
        Ellipse:
            pos: -self.radius, self.radius - self.radius / 2.
            size: self.radius / 2., self.radius / 2.
        Ellipse:
            pos: self.radius - self.radius / 2., self.radius - self.radius / 2.
            size: self.radius / 2., self.radius / 2.
        PopMatrix

    Label:
        text: 'P{} {}'.format(root.index + 1, root.score)
        font_size: 30
        size_hint: None, None
        text_size: 300, None
        y: 820
        x: 100 + root.index * 300

<Bonus>:
    canvas:
        Color:
            rgb: 1, 1, 1
        Rectangle:
            source: root.source
            size: root.radius * 2, root.radius * 2
            pos: root.pos[0] - root.radius, root.pos[1] - root.radius

<BonusPlus>:
    source: 'plus.png'
<BonusFast>:
    source: 'car.png'
<BonusSlow>:
    source: 'turtle.png'
<BonusCherry>:
    source: 'cherry.png'
''')


class Player(Widget):
    index = NumericProperty(0)
    dir = NumericProperty(0)
    line = ListProperty([])
    radius = NumericProperty(12)
    color = NumericProperty(0)
    speed = NumericProperty(300.)
    sensitivity = NumericProperty(250);
    tail_size = NumericProperty(50)
    score = NumericProperty(0)

    def update(self, dt, press):
        self.dir += self.sensitivity * (dt if press else -dt)
        v = Vector(self.speed * dt, 0).rotate(self.dir)
        x, y = Vector(*self.pos) + v
        xx = x % self.width
        yy = y % self.height
        if abs(xx - x) > 500 or abs(yy - y) > 500:
            self.line = [xx, yy]
        self.pos = xx, yy
        self.line = (self.line + [xx, yy])[-self.tail_size:]
        #self.score += int(self.speed * dt)


class Bonus(Widget):
    radius = NumericProperty(10)
    source = StringProperty()

    def collide_player(self, player):
        return Vector(*player.pos).distance(Vector(*self.pos)) < player.radius + self.radius

    def use(self, player):
        pass

class BonusPlus(Bonus):
    def use(self, player):
        player.radius += 5

class BonusFast(Bonus):
    def use(self, player):
        player.sensitivity += 50

class BonusSlow(Bonus):
    def use(self, player):
        player.sensitivity = max(50, player.sensitivity - 50)

class BonusCherry(Bonus):
    def use(self, player):
        player.score += 500

class Run(FloatLayout):

    def __init__(self, **kwargs):
       super(Run, self).__init__(**kwargs) 
       self.bonus = []
       Clock.schedule_interval(self.read_gpio, 0)
       Clock.schedule_interval(self.generate_bonus, 1.)
       self.player1 = Player(color=.2, index=0)
       self.add_widget(self.player1)
       self.player2 = Player(color=.5, index=1)
       self.add_widget(self.player2)
       self.players = [self.player1, self.player2]

    def read_gpio(self, dt):
        p1 = RPIO.input(PIN_P1)
        p2 = RPIO.input(PIN_P2)

        self.player1.update(dt, p1)
        self.player2.update(dt, p2)

        for bonus in self.bonus[:]:
            for player in self.players:
                if bonus.collide_player(player):
                    bonus.use(player)
                    self.bonus.remove(bonus)
                    self.remove_widget(bonus)
                    break
                   
    def generate_bonus(self, dt):
        if len(self.bonus) > 10:
            return
        cls = [BonusPlus, BonusFast, BonusSlow, BonusCherry]
        index = randint(0, len(cls) - 1)
        x = self.width * random()
        y = self.height * random()
        bonus = cls[index](pos=(x, y))
        self.bonus.append(bonus)
        self.add_widget(bonus)


class RunGame(App):
    def build(self):
        return Run()

RunGame().run()

