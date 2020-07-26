import mido
import numpy as np
import pyglet
from pyglet.window import key
import sounddevice as sd

SAMPLERATE = 44100
BLOCKSIZE = 1024
CHANNELS = 1
BUFSIZE = 20
AMPLITUDE = 0.2
FREQUENCY = 440
DTYPE = "float32"

def on_midi(msg):
    if msg.type == "note_on":
        on.add(msg.note)
    if msg.type == "note_off":
        on.remove(msg.note)

start_idx = 0

class Oscillator:
    def __init__(self, frequency, amplitude, samplerate, dtype="float32"):
        self.idx = 0
        self.frequency = frequency
        self.amplitude = amplitude
        self.samplerate = samplerate
        self.dtype = dtype

    def next(self, n):
        t = (self.idx + np.arange(n, dtype=self.dtype)) / self.samplerate
        t = t.reshape(-1, 1)
        self.idx += n
        return AMPLITUDE * np.sin(2 * np.pi * self.frequency * t, dtype=self.dtype)

class KeyboardSynth(pyglet.window.Window):
    WIDTH = 600
    HEIGHT = 600
    def __init__(self):
        super(KeyboardSynth, self).__init__(self.WIDTH, self.HEIGHT)
        self.osc = Oscillator(FREQUENCY, AMPLITUDE, SAMPLERATE, DTYPE)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.osc.frequency = 261.6

    def on_key_release(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.osc.frequency = 440

    def cb(self, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        outdata[:] = self.osc.next(frames)


if __name__=="__main__":
    # try:
    #     port = mido.open_input("Launchkey Mini MK3 MIDI Port")
    #     port.callback = on_midi
    # except OSError:
    #     print("no keyboard found")
    # XXX: I removed device - do we really need to specify it? if so, use
    # `python3 -m sounddevice` to list them
    window = KeyboardSynth()
    stream = sd.RawOutputStream(
        samplerate=SAMPLERATE,
        blocksize=BLOCKSIZE,
        channels=CHANNELS,
        dtype=DTYPE,
        callback=window.cb,
    )
    with stream:
        pyglet.app.run()
