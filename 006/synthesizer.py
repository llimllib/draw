import pyglet
import mido
from scales import notes


class Keyboard:
    def __init__(self):
        """A VERY basic semi-realtime synthesizer."""
        self.window = pyglet.window.Window(720, 480)
        instructions = "Press keys on your keyboard to play notes."
        self.instructions = pyglet.text.Label(text=instructions, font_size=20, x=10, y=10)
        self.current_note = pyglet.text.Label(text="", font_size=33, x=50, y=200)

        self.label = ""

        self.note_cache = {}

        @self.window.event
        def on_draw():
            self.window.clear()
            print("setting text")
            self.current_note.text = self.label
            self.label = ""
            self.instructions.draw()
            self.current_note.draw()

    def on_midi(self, msg):
        if msg.type == "clock":
            return
        print(msg)
        if msg.type == "note_on":
            note, freq = notes[msg.note]
            # this segfaults - wtf? ok, rough guess about what's going on here:
            # mido is running in a separate thread and calling this function from
            # that thread, we change the text of the note from another thread and
            # it's not thread safe. So let's dirty the window and set a message to be updated
            self.invalid = True
            self.label = ""
            print(note, freq)
            self.play_note(freq)

    def play_note(self, frequency, length=0.6):
        if frequency in self.note_cache:
            note_wave = self.note_cache[frequency]
            note_wave.play()
        else:
            adsr = pyglet.media.synthesis.ADSREnvelope(0.05, 0.2, 0.1)
            note_wave = pyglet.media.StaticSource(
                pyglet.media.synthesis.Sawtooth(duration=length, frequency=frequency, envelope=adsr))
            self.note_cache[frequency] = note_wave
            note_wave.play()


if __name__ == "__main__":
    keyboard = Keyboard()
    port = mido.open_input("Launchkey Mini MK3 MIDI Port")
    port.callback = keyboard.on_midi
    pyglet.app.run()
