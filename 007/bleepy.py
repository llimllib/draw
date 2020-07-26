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

def sd_callback(outdata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    global start_idx
    t = (start_idx + np.arange(frames, dtype=DTYPE)) / SAMPLERATE
    t = t.reshape(-1, 1)
    print(FREQUENCY, id(FREQUENCY))
    try:
        outdata[:] = AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t, dtype=DTYPE)
    except ValueError:
        print(len(outdata), len(t), t.shape, t.dtype, t)
        raise
    start_idx += frames

class KeyboardSynth(pyglet.window.Window):
    WIDTH = 600
    HEIGHT = 600
    def __init__(self):
        super(KeyboardSynth, self).__init__(self.WIDTH, self.HEIGHT)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            print("lower")
            global FREQUENCY
            FREQUENCY = 261.6

    def on_key_release(self, symbol, modifiers):
        if symbol == key.SPACE:
            print("higher")
            global FREQUENCY
            FREQUENCY = 440


if __name__=="__main__":
    # try:
    #     port = mido.open_input("Launchkey Mini MK3 MIDI Port")
    #     port.callback = on_midi
    # except OSError:
    #     print("no keyboard found")
    # XXX: I removed device - do we really need to specify it? if so, use
    # `python3 -m sounddevice` to list them
    stream = sd.RawOutputStream(
        samplerate=SAMPLERATE,
        blocksize=BLOCKSIZE,
        channels=CHANNELS,
        dtype=DTYPE,
        callback=sd_callback,
    )
    with stream:
        window = KeyboardSynth()
        pyglet.app.run()
