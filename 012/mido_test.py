#!/usr/bin/env python
# mido appears not to get pitch or modulation signals. A test:
# https://github.com/mido/mido/blob/master/examples/ports/receive.py
import sys
import mido

if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

try:
    with mido.open_input(portname) as port:
        print("Using {}".format(port))
        print("Waiting for messages...")
        for message in port:
            if message.type == "clock":
                continue
            print("Received {}".format(message))
            sys.stdout.flush()
except KeyboardInterrupt:
    pass
