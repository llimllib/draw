#include "livecode.orc"
sr={SAMPLERATE}
ksmps=32
nchnls=2
0dbfs=1

; p4 freq
; p5 amplitude
instr asub
    ; set the k-var `kmoogres` to the "resonance" channel's value.
    kmoogres=0.5 ; I think this works for setting the default resonance? maybe?
    kmoogres chnget "resonance"
    kenv linsegr 0, .05, 1, .05, .9, .8, 0

    aout vco2 p5 * kenv, p4
    aout moogladder aout, 2000, kmoogres
    outs aout, aout
endin

; instrument based on Sub1
instr bsub
  asig = vco2(ampdbfs(-12), p4)
  asig += vco2(ampdbfs(-12), p4 * 1.01, 10)
  asig += vco2(ampdbfs(-12), p4 * 2, 10)
  asig = zdf_ladder(asig, expsegr(10000, 1, 400, .1, 400), 5)
  pan_verb_mix(asig, xchan:i("2.pan", 0.5), xchan:i("2.rvb", chnget:i("rvb.default")))
endin

; based on Sub2
instr csub
  icut = xchan:i("3.cut", sr / 3)
  asig = vco2(ampdbfs(-12), p4) 
  asig += vco2(ampdbfs(-12), p4 * 1.5) 
  asig = zdf_ladder(asig, expsegr(icut, 1, 400, .1, 400), 5)
  pan_verb_mix(asig, xchan:i("3.pan", 0.5), xchan:i("3.rvb", chnget:i("rvb.default")))
endin

; based on Sub4
instr dsub
  asig = vco2(p5, p4)
  asig += vco2(p5, p4 * 1.01)
  asig += vco2(p5, p4 * 0.995)
  asig *= 0.33 
  asig = zdf_ladder(asig, expsegr(100, 1, 22000, 1, 100), 12)
  pan_verb_mix(asig, xchan:i("Sub3.pan", 0.5), xchan:i("Sub3.rvb", chnget:i("rvb.default")))
endin

instr esub
  asig = vco2(p5, p4)
  asig += vco2(p5, p4 * 1.01)
  asig += vco2(p5, p4 * 0.995)
  asig *= 0.33 
  asig = zdf_ladder(asig, expsegr(100, 1, 22000, 1, 100), 12)
  pan_verb_mix(asig, xchan:i("Sub3.pan", 0.5), xchan:i("Sub3.rvb", chnget:i("rvb.default")))
endin

; based on 'Click'. docs:
/**
 * Bandpass-filtered impulse glitchy click sound. p4 = center frequency (e.g.,
 * 3000, 6000) */
instr click2
  asig = mpulse(1, 0)
  outs asig, asig
  ; asig = zdf_2pole(asig, p4, 3, 3)
  ; ; printf "%f %f", 1, p4, p5
  ; asig *= p5 * 4      ;; adjust amp 
  ; asig *= linen:a(1, 0, 1, 0.01) ; p3 is negative

  ;pan_verb_mix(asig, xchan:i("Click.pan", 0.5), xchan:i("Click.rvb", chnget:i("rvb.default")))
endin
