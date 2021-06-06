#!/usr/bin/env python3

import backoff
import colorama
from collections import namedtuple
import subprocess
import time
import sys
import os
import shutil
import tempfile
from gpiozero import Button
import signal
import yaml


CONFIG_PATH = os.path.expanduser("~/.config/radiopi")
STREAM_HISTORY_PATH = os.path.join(CONFIG_PATH, "history")

BUTTON_GPIO_PIN = "GPIO16" # https://pinout.xyz/

delay = 1

class StreamPlayException(Exception):
    pass

Stream = namedtuple('Stream', ['name', 'url'])

class RadioPlayer():

    def __init__(self):
        self._current_stream = None
        self._player_process = None
        self._init_config()

    def _init_config(self):
        if not os.path.exists(CONFIG_PATH):
            os.makedirs(CONFIG_PATH)
        else:
            with open(os.path.join(CONFIG_PATH, 'streams.yaml'), 'r') as config_file:
                try:
                    parsed_yaml = yaml.safe_load(config_file)
                    self.streams = [Stream(**s) for s in parsed_yaml['streams']]
                except yaml.YAMLError as exc:
                    print(exc)

    def set_stream(self, stream):
        index = int(stream)
        self._current_stream = self.streams[index]
        was_running = self.is_running()
        self.stop()
        # self._update_stream_history(stream)
        if was_running:
            self.start()

    @backoff.on_exception(backoff.expo, StreamPlayException, max_time=60)
    def start(self):
        if not self.current_stream():
            raise StreamPlayException("No stream set, cannot start playing")
        stream_url = self.current_stream().url
        print(f"Starting radio player.")
        print(f"Loading stream: {stream_url}")
        args = ["cvlc", stream_url, "vlc://quit"]
        self._player_process = subprocess.Popen(args)
        try:
            self._player_process.wait(timeout=5)
            raise StreamPlayException("Unable to play stream '{stream_url}'")
        except subprocess.TimeoutExpired:
            pass

    def stop(self):
        if self._player_process is not None:
            self._player_process.kill()

    def is_running(self):
        return self._player_process is not None and self._player_process.poll() is None

    def current_stream(self):
        return self._current_stream
        """
        if self.stream_history:
            return self.stream_history[0]
        else:
            return None
        """

    def wait(self):
        if self._player_process:
            return self._player_process.wait()
        return

    """
    def _update_stream_history(self, stream):
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
                streams = []
                for l in lines:
                    try:
                        name, url = l.split(" ")
                        streams.append(Stream(name=name, url=url))
                    except ValueError:
                        streams.append(Stream(name=None, url=url))
                return streams
        except FileNotFoundError:
            return []
    """

def print_available_streams(player):
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}Welcome to RadioPi!{colorama.Style.RESET_ALL}")
    print("Available streams")
    print("=================")
    for idx, stream in enumerate(player.streams):
        if stream.name == player.current_stream().name:
            style = colorama.Style.BRIGHT
            text = f"[{idx}] {stream.name} - {stream.url} [currently listening]"
        else:
            style = colorama.Style.DIM
            text = f"[{idx}] {stream.name} - {stream.url}"
        print(style + text + colorama.Style.RESET_ALL)
    print("=================")

if __name__ == '__main__':
    player = RadioPlayer()
    try:
        station = sys.argv[1]
        player.set_stream(station)
    except IndexError:
        if player.current_stream() is None:
            player.set_stream(0)
    try:
        print_available_streams(player)
        power_button = Button(BUTTON_GPIO_PIN)
        if power_button.is_pressed:
            player.start()
        power_button.when_pressed = lambda: player.start()
        power_button.when_released = lambda: player.stop()
    except:
        print("Failed to set up power button.")
        player.start()
    signal.pause()



