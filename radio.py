#!/usr/bin/env python3

import subprocess
import time
import sys
import os
import shutil
import tempfile

CONFIG_PATH = os.path.expanduser("~/.config/radiopi")
STREAM_HISTORY_PATH = os.path.join(CONFIG_PATH, "history")
DEFAULT_STREAM = "http://radiomeuh.ice.infomaniak.ch/radiomeuh-128.mp3"
delay = 1

def init_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)

def load_stream_history():
    try:
        with open(STREAM_HISTORY_PATH, 'r') as history_file:
            lines = history_file.read().splitlines()
            return lines
    except FileNotFoundError:
        return []

def update_stream_history(stream, history):
    if not history or stream != history[0]:
        new_history = [stream] + history
        with tempfile.TemporaryDirectory() as tempdir:
            new_history_file_path = os.path.join(tempdir, 'history')
            with open(new_history_file_path, 'w') as new_history_file:
                new_history_file.write('\n'.join(new_history))
            shutil.move(new_history_file_path, STREAM_HISTORY_PATH)


def vlc_main_loop(stream_url):
    # Consider using the `backoff` library for better exponential retry delay
    while True:
        print(f"Loading stream: {stream_url}")
        subprocess.run(["cvlc", stream, "vlc://quit"])
        print("Failed to open stream. Relaunching VLC after delay.")
        time.sleep(delay)


if __name__ == '__main__':
    init_config()
    stream_history = load_stream_history()
    try:
        argument = sys.argv[1]
        try:
            stream_index = int(argument)
            stream = stream_history[stream_index]
        except IndexError:
            print("Invalid stream history index")
            sys.exit(1)
        except ValueError:
            stream = argument
    except IndexError:
        try:
            stream = stream_history[0]
        except IndexError:
            stream = DEFAULT_STREAM

    update_stream_history(stream, stream_history)
    vlc_main_loop(stream)
