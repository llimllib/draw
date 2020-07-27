import os
import sys
import threading

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
    key.A: 53,  # F
    key.W: 54,  # F#
    key.S: 55,  # G
    key.E: 56,  # G#
    key.D: 57,  # A
    key.R: 58,  # A#
    key.F: 59,  # B
    key.G: 60,  # C
    key.Y: 61,  # C#
    key.H: 62,  # D
    key.U: 63,  # D#
    key.J: 64,  # E
    key.K: 65,  # F
    key.O: 66,  # F#
    key.L: 67,  # G
    key.P: 68,  # G#
}


class ADSREnvelope:
    def __init__(self, source, attack=100, release=100):
        self.source = source
        self.attack = attack
        # lots of magic vars here
        self.attackspace = np.linspace(0, 1, attack).reshape(attack, 1)

        self.idx = 0

    def next(self, n):
        data = self.source.next(n)
        if self.idx < n:
            data[0 : self.attack] *= self.attackspace
            self.attack
        return data


class Oscillator:
    def __init__(self, frequency, amplitude, samplerate, dtype="float32"):
        self.idx = 0
        self.frequency = frequency
        self.amplitude = amplitude
        self.samplerate = samplerate
        self.dtype = dtype
        self.closed = False

    def close(self):
        self.closed = True

    def next(self, n):
        if self.closed:
            return []

        t = (self.idx + np.arange(n, dtype=self.dtype)) / self.samplerate
        t = t.reshape(-1, 1)
        self.idx += n
        return AMPLITUDE * np.sin(2 * np.pi * self.frequency * t, dtype=self.dtype)


class KeyboardSynth(pyglet.window.Window):
    WIDTH = 600
    HEIGHT = 600

    def __init__(self):
        super(KeyboardSynth, self).__init__(self.WIDTH, self.HEIGHT)
        self.oscs = {}
        self.oscs_lock = threading.RLock()

    def add_osc(self, note):
        with self.oscs_lock:
            self.oscs[note] = ADSREnvelope(
                Oscillator(notes[note][1], AMPLITUDE, SAMPLERATE, DTYPE)
            )

    def rem_osc(self, note):
        with self.oscs_lock:
            del self.oscs[note]

    def on_key_press(self, symbol, modifiers):
        # XXX: this doesn't work. figure out why
        if symbol == key.X:
            pyglet.app.exit()
        if symbol in KEYS:
            self.add_osc(KEYS[symbol])

    def on_key_release(self, symbol, modifiers):
        if symbol in KEYS:
            self.rem_osc(KEYS[symbol])

    def on_midi(self, msg):
        if msg.type == "clock":
            return
        if msg.type == "note_on":
            if msg.note in notes:
                self.add_osc(msg.note)
        if msg.type == "note_off":
            if msg.note in notes:
                self.rem_osc(msg.note)

    def cb(self, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        if not self.oscs:
            outdata[:] = b"\x00" * len(outdata)
        else:
            with self.oscs_lock:
                outdata[:] = np.sum(
                    [o.next(frames) for o in self.oscs.values()], axis=0
                )


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
