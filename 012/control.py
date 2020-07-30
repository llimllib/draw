# This file demonstrates how to use midi codes to control the color of the
# keypads on a Novation LaunchKey mini; There is no official documentation of
# it as far as I can tell
#
# the LaunchKey MK2 Programmer's guide is useful, though not accurate to
# details on the MK3 mini:
# https://customer.novationmusic.com/sites/customer/files/novation/downloads/10535/launchkey-mk2-programmers-reference-guide.pdf

import random
import time

# pip install mido (https://mido.readthedocs.io)
import mido


# when communicating with the novation, "note" is used to represent the pad
# you're changing (or "12" for control codes). Velocity is used for the color
# to set the pad, and channel is the type of color to use. 9 = solid color, 10
# = blink, 11 = pulse
def sendNote(port, channel, note, velocity):
    port.send(mido.Message("note_on", channel=channel, note=note, velocity=velocity))


# useful in interactive prompt
def reset(port):
    # exit extended mode
    sendNote(port, 15, 12, 0)
    # enter extended mode
    sendNote(port, 15, 12, 127)


# the key codes ("notes") for the bottom and top drum pad rows
toprow = [40, 41, 42, 43, 48, 49, 50, 51]
botrow = [36, 37, 38, 39, 44, 45, 46, 47]


def scanAllColors(port):
    # send the "assume control" message; the MK2 documentation calls this
    # "entering extended mode"
    sendNote(port, 15, 12, 127)

    # check out the MK2 programmer's manual linked above for a graphic
    # demonstrating what colors are available
    for color in range(127):
        reset(port)
        sendNote(port, 9, toprow[color % 8], color)
        sendNote(port, 9, botrow[7 - (color % 8)], 127 - color)
        time.sleep(0.05)


def flashingColors(port):
    # assume control
    sendNote(port, 15, 12, 127)

    # channel 10 flashes the pad
    for _ in range(127):
        pad = random.choice(toprow + botrow)
        sendNote(port, 10, pad, random.randint(0, 127))
        time.sleep(0.05)


def pulsingColors(port):
    # assume control
    sendNote(port, 15, 12, 127)

    # channel 11 pulses the pad
    for _ in range(127):
        pad = random.choice(toprow + botrow)
        sendNote(port, 11, pad, random.randint(0, 127))
        time.sleep(0.05)


if __name__ == "__main__":
    # there are two midi ports exposed by the LaunchKey; one for input and one
    # for output. This one is for input, and may have a different name on your
    # system
    port = mido.open_output("Launchkey Mini MK3 DAW Port")
    reset(port)
    scanAllColors(port)
    flashingColors(port)
    pulsingColors(port)
    reset(port)
