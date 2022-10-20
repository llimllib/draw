draw
----

a series of experiments

- `001`: a ball
- `002`:
- `003`:
- `004`:
- `005`: a breakout game, implemented in pyglet and playable with a midi keyboard's knob
- `006`: a terrible first experiment in making noise
- `007`: figuring out real-time-ish music synthesis
- `008`: trying to remove clicks and pops from my synth
- `009`: trying out csound
- `010`: 
- `011`: 
- `012`: still hacking on csound wrapper, no visualization yet. Stuck on why drums aren't working
- `013`: trying to hack live-reload of orchestra file to decrease cycle time
- `014`: rainbow letter sprayer for AJ
- `015`: bouncy squares for Billy

TODO:
- figure out a reasonable way to be able to import utils

## Note

To get it to build on my mac, I ran it with these environment variables:

```
export DYLD_FRAMEWORK_PATH="$DYLD_FRAMEWORK_PATH:/usr/local/opt/csound/Frameworks"

# https://csound.com/docs/manual/CommandEnvironment.html
export INCDIR="utils"
```
