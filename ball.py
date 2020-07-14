#!/usr/bin/env python
import pyglet
from pyglet import shapes

WIDTH = 960
HEIGHT = 960

RED = (255, 0, 0)

window = pyglet.window.Window(WIDTH, HEIGHT)

# the pyglet documentation strongly suggests to draw with a batch, not an
# individual shape, so, FINE
batch = pyglet.graphics.Batch()

# this needs to be a global variable to avoid being garbage collected
c = shapes.Circle(WIDTH // 2, HEIGHT // 2, HEIGHT // 10, color=RED, batch=batch)


@window.event
def on_draw():
    window.clear()

    batch.draw()


pyglet.app.run()
