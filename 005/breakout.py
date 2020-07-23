#!/usr/bin/env python
from enum import Enum
import math
import pyglet

import mido
from pyglet import event
from pyglet import shapes
from pyglet.window import key

# * smooth motion
# * brick break animation?
# * game won label


def clamp(a, mn, mx):
    return max(min(a, mx), mn)


# colors from my web tut
# "#FF1C0A", "#FFFD0A", "#00A308", "#0008DB", "#EB0093"
# def hex2tup(hex_):
#     return (int(hex_[1:3], 16), int(hex_[3:5], 16), int(hex_[5:7], 16))
brickcolors = {
    "red": (255, 28, 10),
    "yellow": (255, 253, 10),
    "green": (0, 163, 8),
    "blue": (0, 8, 219),
    "magenta": (235, 0, 147),
}


class Ball(shapes.Circle):
    RADIUS = 6
    HALF_RADIUS = 5

    def __init__(self, x, y, max_width, max_height, color=(255, 255, 255), batch=None):
        super(Ball, self).__init__(
            x, y, self.RADIUS, color=color, batch=batch, segments=10
        )
        self._radius = self.RADIUS

        self.max_width = max_width
        self.max_height = max_height

        self.max_x_velocity = max_width / 8

        self.x_velocity = max_width / 10
        self.y_velocity = -max_height / 1.5

    # XXX: deleteme?
    def _update_position(self):
        super(Ball, self)._update_position()

    def update(self, dt):
        hit_bottom = False
        if (self.x + self.HALF_RADIUS) > self.max_width and self.x_velocity > 0:
            self.x_velocity *= -1
        if (self.x - self.HALF_RADIUS) < 0 and self.x_velocity < 0:
            self.x_velocity *= -1
        if (self.y + self.HALF_RADIUS) > self.max_height and self.y_velocity > 0:
            self.y_velocity *= -1
        if (self.y - self.HALF_RADIUS) < 0 and self.y_velocity < 0:
            self.y_velocity *= -1
            hit_bottom = True

        self.x += dt * self.x_velocity
        self.y += dt * self.y_velocity

        if hit_bottom:
            return self.x, self.y, True
        return self.x, self.y, False


class Paddle(shapes.Rectangle):
    WIDTH = 100
    HEIGHT = 20

    HW = WIDTH / 2

    def __init__(self, x, y, color=(128, 128, 128), batch=None):
        super(Paddle, self).__init__(x, y, self.WIDTH, self.HEIGHT, color, batch)

    # Paddle.cx is the center of the paddle
    @property
    def cx(self):
        return self.x + self.HW


class Brick(shapes.Rectangle):
    HEIGHT = 20

    def __init__(self, x, y, width, color=(128, 128, 128), batch=None):
        super(Brick, self).__init__(x, y, width, self.HEIGHT, color, batch)

    def break_(self):
        # XXX: I dunno, display a boom or something?
        pass


class BreakoutWindow(pyglet.window.Window):
    # keep a copy of the global width and height
    WIDTH = 600
    HEIGHT = 600

    CENTERX = WIDTH * 0.5
    CENTERY = HEIGHT * 0.5

    # margin between the left of the window and the first brick, and the right
    # of the window and the last brick
    MARGIN = 10
    # padding between bricks
    PADDING = 10

    # if you wait for the ball to actually hit the paddle/bricks, it gives an
    # unpleasant sensation. Anticipate the hit by this many pixels
    HIT_PADDING = 10

    PADDLE_RATE = 400

    COLUMNS = 5

    # WAITING -> PLAYING -> OVER
    #               ^--------|
    WAITING = "WAITING"
    PLAYING = "PLAYING"
    OVER = "OVER"

    BALL_X_START = CENTERX
    BALL_Y_START = 2 * HEIGHT / 3

    def __init__(self):
        super(BreakoutWindow, self).__init__(self.WIDTH, self.HEIGHT)

        self.context.config.sample_buffers = 8

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
            self.BALL_X_START,
            self.BALL_Y_START,
            self.WIDTH,
            self.HEIGHT,
            color=(255, 255, 255),
            batch=self.batch,
        )

        self.paddle = Paddle(self.CENTERX - (Paddle.WIDTH / 2), 0, batch=self.batch)
        self.createbricks()

        # XXX: forward this responsibility to paddle?
        self.left_is_down = False
        self.right_is_down = False

        self.waiting_label = pyglet.text.Label(
            "Press space to play",
            font_size=self.WIDTH * 0.06,
            x=self.CENTERX,
            y=self.CENTERY,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch,
        )
        self.game_over_label = pyglet.text.Label(
            "GAME OVER",
            font_size=self.WIDTH * 0.1,
            x=self.CENTERX,
            y=-1000,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch,
        )

        self.game_state = self.WAITING

        self.mousex = None
        self.midix = None
        self.mididx = 0

        pyglet.clock.schedule_interval(self.update, 1 / 60)

    def reset(self):
        self.createbricks()
        self.ball.delete()
        self.ball = Ball(
            self.BALL_X_START,
            self.BALL_Y_START,
            self.WIDTH,
            self.HEIGHT,
            color=(255, 255, 255),
            batch=self.batch,
        )
        self.paddle.delete()
        self.paddle = Paddle(self.CENTERX - (Paddle.WIDTH / 2), 0, batch=self.batch)

    def createbricks(self):
        self.bricks = []

        brickwidth = (
            self.WIDTH - 2 * self.MARGIN - (self.COLUMNS - 1) * self.PADDING
        ) / self.COLUMNS
        self.bricks = []
        for row, color in enumerate(brickcolors.values()):
            rowy = self.HEIGHT - Brick.HEIGHT - self.MARGIN - row * (Brick.HEIGHT + 5)
            for col in range(self.COLUMNS):
                self.bricks.append(
                    Brick(
                        self.MARGIN + col * (brickwidth + self.PADDING),
                        rowy,
                        brickwidth,
                        color=color,
                        batch=self.batch,
                    )
                )

    def on_key_press(self, symbol, modifiers):
        if self.game_state in self.WAITING:
            if symbol == key.SPACE:
                self.game_state = self.PLAYING
                self.waiting_label.y = -1000
        elif self.game_state == self.OVER:
            if symbol == key.SPACE:
                self.reset()
                self.game_state = self.PLAYING
                self.game_over_label.y = -1000
        elif self.game_state == self.PLAYING:
            if symbol == key.LEFT:
                self.left_is_down = True
            if symbol == key.RIGHT:
                self.right_is_down = True

        # press x to quit
        if symbol == key.X:
            pyglet.app.exit()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.LEFT:
            self.left_is_down = False
        if symbol == key.RIGHT:
            self.right_is_down = False

    def on_mouse_motion(self, x, y, dx, dy):
        self.mousex = x

    def on_midi(self, msg):
        if msg.type == "clock":
            return
        if msg.type == "control_change":
            if not self.midix:
                self.midix = msg.value
            else:
                self.mididx = msg.value - self.midix
                self.midix = msg.value

    # the ball has hit the paddle - adjust its velocity
    # bx is the x position of the ball.
    # paddle is the paddle it's hit
    def bounce(self):
        # distance from the center of the paddle. negative on the left,
        # positive on the right
        dx = self.ball.x - self.paddle.cx
        pct = dx / (self.paddle.WIDTH * 0.5)
        self.ball.x_velocity = pct * (
            self.WIDTH * 0.8
        )  # XXX: give this change value a name
        self.ball.y_velocity *= -1

    def update(self, dt):
        self.clear()

        if self.game_state == self.PLAYING:
            if self.left_is_down:
                if self.paddle.x > 0:
                    self.paddle.x -= dt * self.PADDLE_RATE
            elif self.right_is_down:
                if self.paddle.x < self.WIDTH - self.paddle.WIDTH:
                    self.paddle.x += dt * self.PADDLE_RATE
            elif self.mousex is not None:
                # the difference between the desired paddle x and the current paddle x
                dx = self.mousex - (self.paddle.x + self.paddle.WIDTH / 2)
                if abs(dx) > 1:
                    self.paddle.x += dx * dt * 10
                else:
                    self.mousex = None
            elif self.mididx:
                self.paddle.x += self.mididx * (self.WIDTH / 32)
                self.paddle.x = clamp(
                    self.paddle.x, 0 - self.paddle.HW, self.WIDTH - self.paddle.HW
                )
                self.mididx = 0

            bx, by, hit_bottom = self.ball.update(dt)
            if hit_bottom:
                if not self.paddle.x < bx < self.paddle.x + self.paddle.WIDTH:
                    self.game_state = self.OVER
                    self.game_over_label.y = self.WIDTH / 2

            for i, brick in enumerate(self.bricks):
                if (
                    brick.x < bx < brick.x + brick.width
                    and brick.y
                    < by + math.copysign(self.HIT_PADDING, self.ball.y_velocity)
                    < brick.y + brick.height
                ):
                    brick.break_()
                    self.ball.y_velocity *= -1
                    del self.bricks[i]

            # if we're above the paddle, bounce before we reach the bottom
            # TODO: does not currently work
            if (
                self.paddle.x < bx < self.paddle.x + self.paddle.WIDTH
                and 0 < by - self.HIT_PADDING < self.paddle.HEIGHT
                and self.ball.y_velocity < 0
            ):
                self.bounce()

        # add an FPS meter
        self.fps.text = f"{pyglet.clock.get_fps():0.0f}"

        self.batch.draw()


if __name__ == "__main__":
    _breakout_window = BreakoutWindow()
    port = mido.open_input("Launchkey Mini MK3 MIDI Port")
    port.callback = _breakout_window.on_midi
    pyglet.app.run()
