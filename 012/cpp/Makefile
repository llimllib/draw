all:
	g++ -Wall -D__MACOSX_CORE__ \
		-o midiprobe \
		test.cpp RtMidi.cpp \
		-framework CoreMIDI \
		-framework CoreAudio \
		-framework CoreFoundation
