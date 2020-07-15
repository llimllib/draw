#!/usr/bin/env python
from enum import Enum
import math
import pyglet
from pyglet import shapes


class Color(Enum):
    RED = (255, 0, 0)


# return a if mn < a < mx, mn if a < mn, mx if a > mx
def clamp(a, mn, mx):
    return max(min(a, mx), mn)


class Ball(shapes.Circle):
    MIN_RADIUS = 2
    MAX_RADIUS = 200

    def __init__(self, x, y, color=(255, 255, 255), batch=None):
        # If you start it small and then scale it up, it looks awful because
        # we're not redrawing it or something. not gonna bother figuring it out
        # right now, so start it at 60
        self._radius = 60

        super(Ball, self).__init__(x, y, self.radius, color=color, batch=batch)

    @property
    def radius(self):
        """The radius of the circle.

        :type: float
        """
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = clamp(value, self.MIN_RADIUS, self.MAX_RADIUS)


class SpinnerWindow(pyglet.window.Window):
    WIDTH = 960
    HEIGHT = 960

    CENTERX = WIDTH * 0.5
    CENTERY = HEIGHT * 0.5

    MARGIN = 150

    def __init__(self):
        super(SpinnerWindow, self).__init__(self.WIDTH, self.HEIGHT)

        self.batch = pyglet.graphics.Batch()
        self.fps = pyglet.text.Label(
            "0",
            font_size=12,
            x=20,
            y=40,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch,
        )
        self.ball = Ball(
            self.CENTERX,
            self.HEIGHT - self.MARGIN,
            color=Color.RED.value,
            batch=self.batch,
        )

        pyglet.clock.schedule_interval(self.update, 1 / 60)

    def on_mouse_scroll(self, _, __, ___, scroll_y):
        self.ball.radius = self.ball.radius + scroll_y

    def update(self, dt):
        window.clear()

        # the radius of the circle we're rotating around
        r = min(self.WIDTH, self.HEIGHT) * 0.5 - self.MARGIN

        # rotation speed given in radians per second
        rot = math.pi / 4

        # the circle is currently at (x0, y0), and has angle a from the x-axis.
        # First step is to find a with atan2
        a = math.atan2(self.ball.y - self.CENTERY, self.ball.x - self.CENTERX)

        # then (x1, y1) is (cos(a-dt), sin(a-dt)) scaled by our rotational constant
        # and the radius of the circle
        self.ball.x = self.CENTERX + math.cos(a - dt * rot) * r
        self.ball.y = self.CENTERY + math.sin(a - dt * rot) * r

        # add an FPS meter
        self.fps.text = f"{pyglet.clock.get_fps():0.0f}"

        self.batch.draw()


if __name__ == "__main__":
    window = SpinnerWindow()
    pyglet.app.run()
