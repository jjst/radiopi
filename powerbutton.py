import gpiozero
import datetime
import time
from gpiozero import Button


BUTTON_GPIO_PIN = "GPIO16"  # https://pinout.xyz/

SHORT_PRESS_SECONDS = 1

class PowerButton():

    def __init__(self, player, pin=BUTTON_GPIO_PIN):
        self.last_time_pressed = None
        self.button = Button(BUTTON_GPIO_PIN)
        self.player = player
        if self.button.is_pressed:
            self.player.start()
        self.button.when_pressed = lambda: self._when_pressed()
        self.button.when_released = lambda: player.stop()

    def _when_pressed(self):
        if self.last_time_pressed and (time.monotonic() - self.last_time_pressed) < SHORT_PRESS_SECONDS:
            print("Detected a short press")
        self.last_time_pressed = time.monotonic()
        self.player.start()
