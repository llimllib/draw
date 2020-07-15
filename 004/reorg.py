#!/usr/bin/env python
import math
import pyglet
from pyglet import shapes

WIDTH = 960
HEIGHT = 960

CENTERX = WIDTH * 0.5
CENTERY = HEIGHT * 0.5

# the radius of the red ball. If you start it small and then scale it up, it
# looks awful because we're not redrawing it or something. not gonna bother
# figuring it out right now.
START_RADIUS = 60
MIN_RADIUS = 2
MAX_RADIUS = 200

MARGIN = 150

RED = (255, 0, 0)

window = pyglet.window.Window(WIDTH, HEIGHT)

batch = pyglet.graphics.Batch()
c = shapes.Circle(CENTERX, HEIGHT - MARGIN, START_RADIUS, color=RED, batch=batch)
fps = pyglet.text.Label(
    "0", font_size=12, x=20, y=40, anchor_x="center", anchor_y="center", batch=batch
)


# The dt, or delta time parameter gives the number of “wall clock” seconds
# elapsed since the last call of this function, (or the time the function was
# scheduled, if it’s the first period). Due to latency, load and timer
# inprecision, this might be slightly more or less than the requested interval.
@window.event
def update(dt):
    window.clear()
    global c

    # the radius of the circle we're rotating around
    r = min(WIDTH, HEIGHT) * 0.5 - MARGIN

    # rotation speed given in radians per second
    rot = math.pi / 4

    # the circle is currently at (x0, y0), and has angle a from the x-axis.
    # First step is to find a with atan2
    a = math.atan2(c.y - CENTERY, c.x - CENTERX)

    # then (x1, y1) is (cos(a-dt), sin(a-dt)) scaled by our rotational constant
    # and the radius of the circle
    c.x = CENTERX + math.cos(a - dt * rot) * r
    c.y = CENTERY + math.sin(a - dt * rot) * r

    # add an FPS meter
    fps.text = f"{pyglet.clock.get_fps():0.0f}"

    batch.draw()


# return a if mn < a < mx, mn if a < mn, mx if a > mx
def clamp(a, mn, mx):
    return max(min(a, mx), mn)


# let the user resize the ball with the scroll wheel. Especially with the touch
# pad, this could use some debouncing I think
@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    c.radius = clamp(c.radius + scroll_y, MIN_RADIUS, MAX_RADIUS)


pyglet.clock.schedule_interval(update, 1 / 60)
pyglet.app.run()
