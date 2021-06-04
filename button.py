from gpiozero import Button
from signal import pause

button = Button("GPIO17")

button.when_pressed = lambda: print("Pressed")
button.when_released = lambda: print("Released")

pause()
