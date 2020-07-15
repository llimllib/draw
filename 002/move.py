#!/usr/bin/env python
import math
import pyglet
from pyglet import shapes

WIDTH = 960
HEIGHT = 960

MARGIN = 100

RED = (255, 0, 0)

window = pyglet.window.Window(WIDTH, HEIGHT)

# the pyglet documentation strongly suggests to draw with a batch, not an
# individual shape, so, FINE
batch = pyglet.graphics.Batch()

# this needs to be a global variable to avoid being garbage collected
c = shapes.Circle(WIDTH // 2, HEIGHT // 2, HEIGHT // 10, color=RED, batch=batch)

# let's tick time. I should rely on the `dt` variable, which will allow us to
# continue at the right point even if we missed some frames, but that requires
# some thought. Let's just get something moving. Good >> perfect
t = 0


# The dt, or delta time parameter gives the number of “wall clock” seconds
# elapsed since the last call of this function, (or the time the function was
# scheduled, if it’s the first period).
# https://pyglet.readthedocs.io/en/latest/programming_guide/time.html#guide-calling-functions-periodically
@window.event
def update(dt):
    window.clear()
    global t, c

    slow = 0.01

    # update our circle's position
    c.x = WIDTH * 0.5 + math.sin(t * slow) * (WIDTH * 0.5 - MARGIN)
    c.y = HEIGHT * 0.5 + math.cos(t * slow) * (HEIGHT * 0.5 - MARGIN)
    t += 1

    batch.draw()


pyglet.clock.schedule_interval(update, 1 / 60)
pyglet.app.run()
