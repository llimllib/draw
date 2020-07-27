from math import ceil
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
# TODO: choose between instruments and show it on the UI


class KeyboardSynth(pyglet.window.Window):
    WIDTH = 600
    HEIGHT = 600

    def __init__(self, csound):
        super(KeyboardSynth, self).__init__(self.WIDTH, self.HEIGHT)
        self.cs = csound
        self.cs.setOption("-odac")
        self.cs.setOption("-m6")
        orc = f"""
#include "livecode.orc"
sr={SAMPLERATE}
ksmps=32
nchnls=2
0dbfs=1

; p4 freq
; p5 amplitude
instr 1 
    ; set the k-var `kmoogres` to the "resonance" channel's value.
    kmoogres=0.5 ; I think this works for setting the default resonance? maybe?
    kmoogres chnget "resonance"
    kenv linsegr 0, .05, 1, .05, .9, .8, 0

    aout vco2 p5 * kenv, p4
    aout moogladder aout, 2000, kmoogres
    outs aout, aout
endin

; instrument based on Sub1
instr 2
  asig = vco2(ampdbfs(-12), p4)
  asig += vco2(ampdbfs(-12), p4 * 1.01, 10)
  asig += vco2(ampdbfs(-12), p4 * 2, 10)
  ; the provided implementation of Sub1 gives the duration here
  ;   the second parameter of zdf_ladder represents the cutoff frequency
  ;   (I don't _really_ know what this means, tbh)
  ;     expon(start, dur, end) traces an exponential curve between the given points - so here we're telling zdf_ladder that its cutoff starts at 10000, and decreases to 400 at the given duration.
  ;     The problem is of course that we're playing the notes live so there is no known duration - let's just set it to 1. Possibly add a default to livecode?
  asig = zdf_ladder(asig, 1000, 5)
  pan_verb_mix(asig, xchan:i("2.pan", 0.5), xchan:i("2.rvb", chnget:i("rvb.default")))
endin

; based on Sub2
instr 3
  asig = vco2(ampdbfs(-12), p4) 
  asig += vco2(ampdbfs(-12), p4 * 1.5) 
  ; TODO: set the 10000 to a channel that can be set
  asig = zdf_ladder(asig, 10000, 5)
  pan_verb_mix(asig, xchan:i("3.pan", 0.5), xchan:i("3.rvb", chnget:i("rvb.default")))
endin

; based on Sub4
instr 4
  asig = vco2(p5, p4)
  asig += vco2(p5, p4 * 1.01)
  asig += vco2(p5, p4 * 0.995)
  asig *= 0.33 
  ; so, I have to comment this out, but it's the heart of this synth:
  ; How tdo I have a function that goes exponentially like this, but then
  ; _holds_ at the endpoint? So, say: 100 -> 22000 over one second, then
  ; hold indefinitely?
  ; asig = zdf_ladder(asig, expon(100, 1, 22000), 12)
  ; Steven Yi (!) responded to my message and suggested something like this:
  asig = zdf_ladder(asig, expsegr(100, 1, 22000, 1, 100), 12)
  ; asig = moogladder(asig, 22000, 0.5)
  pan_verb_mix(asig, xchan:i("Sub3.pan", 0.5), xchan:i("Sub3.rvb", chnget:i("rvb.default")))
endin
"""
        if self.cs.compileOrc(orc) != 0:
            print("failed to compile orchestra")
            self.close()
            pyglet.app.exit()
        self.cs.start()
        self.t = CsoundPerformanceThread(self.cs.csound())
        self.t.play()
        self.instrument = 1
        self.n_instruments = 4

        # # pyglet stuff
        self.batch = pyglet.graphics.Batch()
        self.notes = []
        self.gltext = f"instrument {self.instrument}"
        self.general_label = pyglet.text.Label(
            self.gltext,
            font_size=self.WIDTH * 0.06,
            x=self.WIDTH * 0.5,
            y=self.HEIGHT * 0.5,
            anchor_x="center",
            anchor_y="center",
            batch=self.batch,
        )

        pyglet.clock.schedule_interval(self.update, 1 / 60)

    def on_key_press(self, symbol, modifiers):
        # press x to quit
        if symbol == key.X:
            pyglet.app.exit()

    def on_key_release(self, symbol, modifiers):
        pass

    def on_midi(self, msg):
        if msg.type == "clock":
            return
        elif msg.type == "note_on":
            print(msg)
            self.notes.append(notes[msg.note][0])
            self.gltext = ", ".join(self.notes)
            cmsg = f"i {self.instrument}.{msg.note} 0 -1 {notes[msg.note][1]} {msg.velocity/255:.2}"
            print(cmsg)
            self.t.inputMessage(cmsg)
        elif msg.type == "note_off":
            self.notes.remove(notes[msg.note][0])
            self.gltext = ", ".join(self.notes)
            cmsg = f"i -{self.instrument}.{msg.note} 0 -1"
            print(cmsg)
            self.t.inputMessage(cmsg)
        elif msg.type == "control_change":
            if msg.control == 21:
                self.instrument = ceil(msg.value / (127 / self.n_instruments))
                print(f"new instrument {self.instrument}")
                self.gltext = f"instrument {self.instrument}"
            # XXX: how to map pots to different channels depending on the
            # active instrument?
            elif msg.control == 22:
                print(msg, msg.value / 127)
                self.cs.setControlChannel("resonance", msg.value / 127)

    def on_daw(self, msg):
        if msg.type == "clock":
            return
        print(msg)

    def on_close(self):
        self.t.stop()
        super(KeyboardSynth, self).on_close()

    def update(self, dt):
        self.clear()
        self.general_label.text = self.gltext
        self.batch.draw()


if __name__ == "__main__":
    try:
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
            main()
        pyglet.app.run()
    finally:
        cs.stop()
        cs.cleanup()
        cs.reset()

        if port:
            port.close()
        if port2:
            port2.close()

    sys.exit(0)
