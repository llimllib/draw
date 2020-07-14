#!/usr/bin/env python
import math
import pyglet
from pyglet import shapes

WIDTH = 960
HEIGHT = 960

START_RADIUS = 10
MIN_RADIUS = 2
MAX_RADIUS = 20

MARGIN = 100

RED = (255, 0, 0)

window = pyglet.window.Window(WIDTH, HEIGHT)

batch = pyglet.graphics.Batch()
c = shapes.Circle(WIDTH // 2, HEIGHT // 2, START_RADIUS, color=RED, batch=batch)


@window.event
def update(dt):
    window.clear()
    global c

    # rotation speed given in radians per second
    rot = 2 * math.pi

    c.x = WIDTH * 0.5 + math.sin(dt * rot) * (WIDTH * 0.5 - MARGIN)
    c.y = HEIGHT * 0.5 + math.cos(dt * rot) * (HEIGHT * 0.5 - MARGIN)

    batch.draw()


# return a if mn < a < mx, mn if a < mn, mx if a > mx
def clamp(a, mn, mx):
    return max(min(a, mx), mn)


def on_mouse_scroll(x, y, scroll_x, scroll_y):
    c.radius = clamp(scroll_y, MIN_RADIUS, MAX_RADIUS)
    print("scroll", c.radius)


pyglet.clock.schedule_interval(update, 1 / 60)
pyglet.app.run()
