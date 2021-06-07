import gpiozero
from gpiozero import Button


BUTTON_GPIO_PIN = "GPIO16"  # https://pinout.xyz/

SHORT_PRESS_SECONDS = 1

class PowerButton():

    def __init__(self, player, pin=BUTTON_GPIO_PIN):
        self.button = Button(BUTTON_GPIO_PIN)
        self.player = player
        if self.button.is_pressed:
            self.player.start()
        self.button.when_pressed = lambda: self._when_pressed()
        self.button.when_released = lambda: self._when_released()

    def _when_released(self):
        self.player.stop()

    def _when_pressed(self):
        self.player.start()
