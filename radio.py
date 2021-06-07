#!/usr/bin/env python3

import backoff
from display import Display
from collections import namedtuple
import gpiozero
import subprocess
import sys
import os
import requests
import signal
import yaml

import console
import powerbutton


CONFIG_PATH = os.path.expanduser("~/.config/radiopi")
STREAM_HISTORY_PATH = os.path.join(CONFIG_PATH, "history")
API_URL = os.environ.get("RADIO_API_URL", "https://now-playing-42nq5.ondigitalocean.app/api")


class StreamPlayException(Exception):
    pass


Stream = namedtuple('Stream', ['name', 'url', 'favicon'])


class RadioPlayer():

    def __init__(self, streams, display):
        self.display = display
        self._current_stream = None
        self._player_process = None
        self.streams = streams

    def set_stream(self, stream):
        was_running = self.is_running()
        if self._player_process is not None:
            self._player_process.kill()
        index = int(stream)
        self._current_stream = self.streams[index]
        if self.display and self.is_running():
            self.display.show_stream(self._current_stream.name)
        # self._update_stream_history(stream)
        if was_running:
            self.start()

    @backoff.on_exception(backoff.expo, StreamPlayException, max_time=60)
    def start(self):
        if not self.current_stream():
            raise StreamPlayException("No stream set, cannot start playing")
        if self.display:
            self.display.show_stream(self.current_stream().name)
        stream_url = self.current_stream().url
        print("Starting radio player.")
        print(f"Loading stream: {stream_url}")
        args = ["cvlc", stream_url, "vlc://quit"]
        self._player_process = subprocess.Popen(args)
        try:
            self._player_process.wait(timeout=5)
            raise StreamPlayException("Unable to play stream '{stream_url}'")
        except subprocess.TimeoutExpired:
            pass

    def stop(self):
        if self.display:
            self.display.turn_off()
        if self._player_process is not None:
            self._player_process.kill()

    def is_running(self):
        return self._player_process is not None and self._player_process.poll() is None

    def current_stream(self):
        return self._current_stream

    def wait(self):
        if self._player_process:
            return self._player_process.wait()
        return


def get_available_streams():
    stations = [s for s in requests.get(f"{API_URL}/stations/fr").json()['items'] if s['streams']]
    return [
        Stream(
            name=s['name'],
            url=s['streams'][0]['url'],
            favicon=s['favicon']
        ) for s in stations
    ]


def main():
    streams = get_available_streams()
    try:
        display = Display()
    except OSError:
        console.error("Failed to setup e-ink display.")
        display = None
    player = RadioPlayer(streams, display)
    try:
        station = sys.argv[1]
        player.set_stream(station)
    except IndexError:
        if player.current_stream() is None:
            player.set_stream(0)
    console.print_available_streams(player)
    try:
        power_button = powerbutton.PowerButton(player)
    except gpiozero.exc.BadPinFactory:
        console.error("Failed to set up power button.")
        player.start()
    signal.pause()


if __name__ == '__main__':
    main()
