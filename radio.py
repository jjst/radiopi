#!/usr/bin/env python3

import subprocess
import time
import sys
import os
import shutil
import tempfile
from gpiozero import Button
from signal import pause

CONFIG_PATH = os.path.expanduser("~/.config/radiopi")
STREAM_HISTORY_PATH = os.path.join(CONFIG_PATH, "history")
DEFAULT_STREAM = "http://radiomeuh.ice.infomaniak.ch/radiomeuh-128.mp3"
BUTTON_GPIO_PIN = "GPIO17"

delay = 1

def init_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_PATH)


class RadioPlayer:

    def __init__(self):
        self.stream_history = self._load_stream_history()
        self._player_process = None

    def change_station(self, station):
        try:
            index = int(station)
            stream_url = self.stream_history[index]
        except:
            stream_url = station
        was_running = self.is_running()
        self.stop()
        self._update_stream_history(stream_url)
        if was_running:
            self.start()

    def start(self):
        stream_url = self.current_stream()
        print(f"Starting radio player.")
        print(f"Loading stream: {stream_url}")
        args = ["cvlc", stream_url, "vlc://quit"]
        self._player_process = subprocess.Popen(args)

    def stop(self):
        self._player_process.kill()

    def is_running(self):
        return self._player_process is not None and self._player_process.poll() is None

    def current_stream(self):
        if self.stream_history:
            return self.stream_history[0]
        else:
            return None

    def wait(self):
        if self._player_process:
            return self._player_process.wait()
        return

    def _update_stream_history(self, stream_url):
        if not self.stream_history or stream != self.stream_history[0]:
            self.stream_history = [stream] + self.stream_history
            with tempfile.TemporaryDirectory() as tempdir:
                new_history_file_path = os.path.join(tempdir, 'history')
                with open(new_history_file_path, 'w') as new_history_file:
                    new_history_file.write('\n'.join(self.stream_history))
                shutil.move(new_history_file_path, STREAM_HISTORY_PATH)

    def _load_stream_history(self):
        try:
            with open(STREAM_HISTORY_PATH, 'r') as history_file:
                lines = history_file.read().splitlines()
                return lines
        except FileNotFoundError:
            return []


if __name__ == '__main__':
    init_config()
    player = RadioPlayer()
    try:
        station = sys.argv[1]
        player.change_station(station)
    except IndexError:
        if player.current_stream() is None:
            player.change_station(DEFAULT_STREAM)
    try:
        power_button = Button(BUTTON_GPIO_PIN)
        if power_button.is_pressed:
            player.start()
        power_button.when_pressed = lambda: player.start()
        power_button.when_released = lambda: player.stop()
    except:
        print("Failed to set up power button.")
    player.wait()



