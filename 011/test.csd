<CsoundSynthesizer>
<CsOptions>
-odac -m7 -Ma --midi-key-cps=4 --midi-velocity-amp=5
</CsOptions>
; ==============================================
<CsInstruments>

#include "livecode.orc"

sr	=	48000
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
endin

; schedule("Sub1", 0, 2, 440, 0.5)
</CsInstruments>
; ==============================================
<CsScore>
; i("Sub1", 0, 2, 440, 0.5)
i "Sub1"  0  2  440  0.5


</CsScore>
</CsoundSynthesizer>

