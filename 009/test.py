from ctcsound import Csound, CsoundPerformanceThread

cs = Csound()
cs.setOption("-odac")
cs.setOption("-m7")
# Our Orchestra for our project
orc = """
sr=44100
ksmps=32
nchnls=2
0dbfs=1
gkpch chnexport "freq", 1
instr 1 
kpch port gkpch, 0.01, i(gkpch)
printk .5, gkpch
kenv linsegr 0, .05, 1, .05, .9, .8, 0
aout vco2 p4 * kenv, kpch
aout moogladder aout, 2000, .25 
outs aout, aout
endin"""
cs.compileOrc(orc)
cs.start()
t = CsoundPerformanceThread(cs.csound())
t.play()
t.inputMessage("i1 
