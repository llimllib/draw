# Wahoo this gets us terrible bleepy audio playback! But at least it's not a
# predefined length. Next: figure out how to get reasonably smooth playback
# from notes?
from multiprocessing import Process
import threading
import time

from scales import notes

import mido
import numpy as np
import simpleaudio as sa

on = set()

def on_midi(msg):
    if msg.type == "note_on":
        on.add(msg.note)
    if msg.type == "note_off":
        on.remove(msg.note)

def play():
    sample_rate = 44100
    T = 1/5
    t = np.linspace(0, T, int(T * sample_rate), False)

    while 1:
        waves = []
        for note in on:
            _, freq = notes[note]
            print("appending", freq)
            waves.append(np.sin(freq * t * 2 * np.pi))

        if waves:
            # concatenate notes - this plays one after the other
            # audio = np.hstack(waves)
            # sum the streams to join them
            audio = np.sum(waves, axis=0)

            # normalize to 16-bit range (?)
            audio *= 32767 / np.max(np.abs(audio))
            # convert to 16-bit data
            audio = audio.astype(np.int16)
            # start playback
            play_obj = sa.play_buffer(audio, 1, 2, sample_rate)
            # play_obj.wait_done()
        # else:
        #     time.sleep(T)
        time.sleep(T/2)

def main():
    while 1:
        if on:
            print(on)
        time.sleep(1/60)

if __name__=="__main__":
    port = mido.open_input("Launchkey Mini MK3 MIDI Port")
    port.callback = on_midi
    # p = Process(target=play)
    # p.start()
    t = threading.Thread(target=play)
    t.start()
    main()
