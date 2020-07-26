import os
import sys

import mido
import numpy as np
import pyglet
from pyglet.window import key
import sounddevice as sd

# python relative imports... sigh...
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.notes import notes

SAMPLERATE = 44100
BLOCKSIZE = 1024
CHANNELS = 1
AMPLITUDE = 0.2
FREQUENCY = 440
DTYPE = "float32"


def on_midi(msg):
    if msg.type == "note_on":
        on.add(msg.note)
    if msg.type == "note_off":
        on.remove(msg.note)


KEYS = {
    key.A: 174.614,  # F
    key.W: 184.997,  # F#
    key.S: 195.998,  # G
    key.E: 207.652,  # G#
    key.D: 220.0,  # A
    key.R: 233.082,  # A #
    key.F: 246.942,  # B
    key.G: 261.626,  # C
    key.Y: 277.183,  # C #
    key.H: 293.665,  # D
}


class Oscillator:
    def __init__(self, frequency, amplitude, samplerate, dtype="float32"):
        self.idx = 0
        self.frequency = frequency
        self.amplitude = amplitude
        self.samplerate = samplerate
        self.dtype = dtype

    def next(self, n):
        # XXX: would be good to not allocate any memory here. Can I cheat by
        # knowing the usual number of n?
        t = (self.idx + np.arange(n, dtype=self.dtype)) / self.samplerate
        t = t.reshape(-1, 1)
        self.idx += n
        return AMPLITUDE * np.sin(2 * np.pi * self.frequency * t, dtype=self.dtype)


class KeyboardSynth(pyglet.window.Window):
    WIDTH = 600
    HEIGHT = 600

    def __init__(self):
        super(KeyboardSynth, self).__init__(self.WIDTH, self.HEIGHT)
        self.oscs = []

    def add_osc(self, freq):
        self.oscs.append(Oscillator(freq, AMPLITUDE, SAMPLERATE, DTYPE))

    def rem_osc(self, freq):
        # XXX: float comparisons possibly a problem?
        self.oscs = [o for o in self.oscs if o.frequency != freq]

    def on_key_press(self, symbol, modifiers):
        if symbol in KEYS:
            self.add_osc(KEYS[symbol])

    def on_key_release(self, symbol, modifiers):
        if symbol in KEYS:
            self.rem_osc(KEYS[symbol])

    def on_midi(self, msg):
        # TODO: velocity
        if msg.type == "note_on":
            if msg.note in notes:
                self.add_osc(notes[msg.note][1])
        if msg.type == "note_off":
            if msg.note in notes:
                self.rem_osc(notes[msg.note][1])

    def cb(self, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        if not self.oscs:
            outdata[:] = b"\x00" * len(outdata)
        else:
            outdata[:] = np.sum([o.next(frames) for o in self.oscs], axis=0)


if __name__ == "__main__":
    # XXX: I removed device - do we really need to specify it? if so, use
    # `python3 -m sounddevice` to list them
    window = KeyboardSynth()
    try:
        if [x for x in mido.get_input_names() if "Launchkey" in x]:
            port = mido.open_input("Launchkey Mini MK3 MIDI Port")
            port.callback = window.on_midi
    except OSError:
        print("no keyboard found")
    stream = sd.RawOutputStream(
        samplerate=SAMPLERATE,
        blocksize=BLOCKSIZE,
        channels=CHANNELS,
        dtype=DTYPE,
        callback=window.cb,
    )
    with stream:
        pyglet.app.run()
