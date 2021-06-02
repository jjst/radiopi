#!/usr/bin/env python3

import subprocess
import time
import sys

DEFAULT_STREAM = "http://radiomeuh.ice.infomaniak.ch/radiomeuh-128.mp3"
delay = 1

def vlc_main_loop(stream_url):
    # Consider using the `backoff` library for better exponential retry delay
    while True:
        print(f"Loading stream: {stream_url}")
        subprocess.run(["cvlc", stream, "vlc://quit"])
        print("Failed to open stream. Relaunching VLC after delay.")
        time.sleep(delay)


if __name__ == '__main__':
    try:
        stream = sys.argv[1]
    except IndexError:
        stream = DEFAULT_STREAM

    vlc_main_loop(stream)
