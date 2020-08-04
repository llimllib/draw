#!/usr/bin/env python
from enum import Enum
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

# TODO: play around with some programs! Find more parameters that are settable
# TODO: choose between instruments and show it on the UI
# TODO: pitch wheel
#       when I connect to the keyboard with "midi monitor", it shows the pitch
#       wheel messages coming from the midi port
# TODO: how to read the clock out of csound


class KeyboardSynth(pyglet.window.Window):
    WIDTH = 600
    HEIGHT = 600

    KEYBOARD = 0
    DRUMPAD = 9

    def __init__(self, csound):
        super(KeyboardSynth, self).__init__(self.WIDTH, self.HEIGHT)
        self.cs = csound
        self.cs.setOption("-odac")
        self.cs.setOption("-m6")
        csound_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "a.csd"))
        orc = open(csound_file).read().format(SAMPLERATE=SAMPLERATE)
        if self.cs.compileOrc(orc) != 0:
            print("failed to compile orchestra")
            self.close()
            pyglet.app.exit()
        self.cs.start()
        self.t = CsoundPerformanceThread(self.cs.csound())
        self.t.play()

        # I would _really_ like to find the current value of knob 21, which
        # controls this, at startup, but I don't know how to query the keyboard
        # for its value so we just wait for it to change. I can't figure out
        # how to do this!
        #
        # I would also love to figure out how to call named instruments, but
        # the dot notation doesn't seem to work for them. i.e. I'd love to say
        # 'i "Sub".1 <arguments>' followed by 'i "-Sub".1' to turn it off, but
        # I can't make it work
        self.instrument = 1
        self.n_instruments = 4

        # XXX: I'm also not getting pitch bend or modulation messages. How do I
        # receive those?

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
            if msg.channel == self.KEYBOARD:
                print(msg)
                self.notes.append(notes[msg.note][0])
                self.gltext = ", ".join(self.notes)
                cmsg = f"i {self.instrument}.{msg.note} 0 -1 {notes[msg.note][1]} {msg.velocity/255:.2}"
                print(cmsg)
                self.t.inputMessage(cmsg)
            if msg.channel == self.DRUMPAD:
                print(msg)
                cmsg = f"i 5 0 -1 6000 {msg.velocity/127:.2}"
                print(cmsg)
                self.t.inputMessage(cmsg)
        elif msg.type == "note_off":
            if msg.channel == self.KEYBOARD:
                self.notes.remove(notes[msg.note][0])
                self.gltext = ", ".join(self.notes)
                cmsg = f"i -{self.instrument}.{msg.note} 0 -1"
                print(cmsg)
                self.t.inputMessage(cmsg)
        elif msg.type == "control_change":
            if msg.control == 21:
                ival = ceil(msg.value / (127 / self.n_instruments))
                self.gltext = f"instrument {self.instrument}"
                if self.instrument != ival:
                    self.instrument = ival
                    print(f"new instrument {self.instrument}")
            # XXX: how to map pots to different channels depending on the
            # active instrument?
            elif msg.control == 22:
                print(msg, msg.value / 127)
                self.cs.setControlChannel("resonance", msg.value / 127)
            else:
                print("Unhandled message", msg)
        else:
            print("Unhandled message", msg)

    def on_daw_in(self, msg):
        if msg.type == "clock":
            return
        print("daw input", msg)

    def on_daw_out(self, msg):
        if msg.type == "clock":
            return
        print("daw output", msg)

    def on_close(self):
        self.t.stop()
        super(KeyboardSynth, self).on_close()

    def update(self, dt):
        self.clear()
        self.general_label.text = self.gltext
        self.batch.draw()


if __name__ == "__main__":
    port = None
    daw_in = None
    daw_out = None
    try:
        cs = Csound()
        window = KeyboardSynth(cs)
        try:
            if [x for x in mido.get_input_names() if "Launchkey" in x]:
                port = mido.open_input("Launchkey Mini MK3 MIDI Port")
                port.callback = window.on_midi
                daw_in = mido.open_input("Launchkey Mini MK3 DAW Port")
                daw_in.callback = window.on_daw_in
                daw_out = mido.open_output("Launchkey Mini MK3 DAW Port")
                daw_out.callback = window.on_daw_out

                # enter extended mode. When we do this, all the lights on the
                # keypad go blank, and now the keypads send input on the daw
                # input channel. Also we seem to get the > and stop/solo/mute
                # buttons now. Still no pitch bend and modulation though
                # daw_out.send(mido.Message("note_on", channel=15, note=12, velocity=0))
                # daw_out.send(mido.Message("note_on", channel=15, note=12, velocity=127))
                #
                # OK, I don't think I really need these; I just noticed that
                # the drum pad messages come in on channel 9, while the
                # keyboard is on channel 0 so we can distinguish them that way
                #
                # also pitch wheel messages were coming through and I was
                # throwing them away like a dope
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
        if daw_in:
            daw_in.close()
        if daw_out:
            daw_out.close()

    sys.exit(0)
