import time
import random

from neopixel import *


# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering



# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
	# Intialize the library (must be called once before other functions).
	strip.begin()



class DefaultScript():
	def __init__(self):
		pass

	def update(self):
		pass

	def refresh(self):
		while True:
			yield [Color(0,0,255)] * 16


class TwinkleScript():
	def __init__(self, hue=60):
		self.hue = hue

	def update(self, value):
		self.hue = value

	def refresh(self):
		while True:
			pixels = [None]*16
			for i in range(16):
				pixels[i] = Color.fromHSB(self.hue, random.uniform(0.5,1), 1)
			yield pixels

class Animator():
	def __init__(self, strip):
		self.script = DefaultScript()
		self.strip = strip

	def updateScript(self, script):
		self.script = script

	def run(self):
		while True:
			pixels = script.refresh()

			for i in range(0,16):
				strip.setPixelColor(i, wheel((i+j) & 255))

			strip.show()
			time.sleep(20.0/1000.0)
