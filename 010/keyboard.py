import os
import sys

import mido
import numpy as np
import pyglet
from pyglet.window import key
from ctcsound import Csound, CsoundPerformanceThread

# python relative imports... sigh...
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.notes import notes

SAMPLERATE = 44100

# TODO: figure out what those variables I'm setting at the top mean
# TODO: get the orchestra into a separate file?
# TODO: play around with some programs! Find more parameters that are settable
# TODO: get some UI up and running


def on_midi(msg):
    if msg.type == "note_on":
        on.add(msg.note)
    if msg.type == "note_off":
        on.remove(msg.note)


class KeyboardSynth(pyglet.window.Window):
    WIDTH = 600
    HEIGHT = 600

    def __init__(self, csound):
        super(KeyboardSynth, self).__init__(self.WIDTH, self.HEIGHT)
        self.cs = csound
        self.cs.setOption("-odac")
        self.cs.setOption("-m7")
        orc = f"""
sr={SAMPLERATE}
ksmps=32
nchnls=2
0dbfs=1

; p4 amplitude
; p5 freq
instr 1 
; set the k-var `kmoogres` to the "resonance" channel's value.
kmoogres=0.5 ; I think this works for setting the default resonance? maybe?
kmoogres chnget "resonance"
kenv linsegr 0, .05, 1, .05, .9, .8, 0

aout vco2 p4 * kenv, p5
aout moogladder aout, 2000, kmoogres
outs aout, aout
endin"""
        if self.cs.compileOrc(orc) != 0:
            print("failed to compile orchestra")
            pyglet.app.exit()
        self.cs.start()
        self.t = CsoundPerformanceThread(self.cs.csound())
        self.t.play()
        print("csound initialized")

    def on_key_press(self, symbol, modifiers):
        # press x to quit
        if symbol == key.X:
            pyglet.app.exit()

    def on_key_release(self, symbol, modifiers):
        pass

    def on_midi(self, msg):
        if msg.type == "clock":
            return
        if msg.type == "note_on":
            print(msg)
            # http://www.csounds.com/manual/html/i.html
            # i <instrument> <offset> <duration> [<instrument args>...]
            cmsg = f"i 1.{msg.note} 0 -1 {msg.velocity/255:.2} {notes[msg.note][1]}"
            print(cmsg)
            self.t.inputMessage(cmsg)
        if msg.type == "note_off":
            # You can also turnoff notes from the score by using a negative
            # number for the instrument (p1). This is equivalent to using the
            # turnoff2 opcode. When a note is turned off from the score, it
            # is allowed to release (if xtratim or opcodes with release
            # section like linenr are used) and only notes with the same
            # fractional part are turned off. Also, only the last instance of
            # the instrument will be turned off, so there have to be as many
            # negative instrument numbers as positive ones for all notes to
            # be turned off.
            cmsg = f"i -1.{msg.note} 0 -1"
            print(cmsg)
            self.t.inputMessage(cmsg)

        if msg.type == "control_change":
            print(msg, msg.value / 127)
            self.cs.setControlChannel("resonance", msg.value / 127)

    def on_daw(self, msg):
        if msg.type == "clock":
            return
        print(msg)

    def on_close(self):
        self.t.stop()
        super(KeyboardSynth, self).on_close()


if __name__ == "__main__":
    # XXX: I removed device - do we really need to specify it? if so, use
    # `python3 -m sounddevice` to list them
    cs = Csound()
    window = KeyboardSynth(cs)
    port = None
    port2 = None
    try:
        if [x for x in mido.get_input_names() if "Launchkey" in x]:
            port = mido.open_input("Launchkey Mini MK3 MIDI Port")
            port.callback = window.on_midi
            port2 = mido.open_input("Launchkey Mini MK3 DAW Port")
            port2.callback = window.on_daw
            print("keyboard initialized")
    except OSError:
        print("no keyboard found")
    pyglet.app.run()

    # I don't know how to get these to fire on pyglet closing, but this seems
    # to work :shrug:. I still get segfaults sometimes ahhhhhh
    cs.stop()
    cs.cleanup()
    cs.reset()

    sys.exit(0)
