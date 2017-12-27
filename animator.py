import time
import random
import threading
import colorsys

from neopixel import *

def _initNeoPixels():
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

	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
	# Intialize the library (must be called once before other functions).
	strip.begin()

	return strip

def fromHSV(hue, saturation, value):
	(r,g,b) = [int(255*i) for i in colorsys.hsv_to_rgb(hue, saturation, value)]
	return Color(r,g,b)


class DefaultScript():
	def __init__(self):
		pass

	def update(self):
		pass

	def refresh(self):
		return [Color(0,0,255)] * 16


class TwinkleScript():
	def __init__(self, hue=60):
		self.hue = hue

	def update(self, value):
		self.hue = value

	def refresh(self):
		return [fromHSV(self.hue/360.0, random.uniform(0.9,1), .4) for i in range(0,16)]


class NotRandomScript():
	def __init__(self, hue=60):
		self.hue = hue

	def update(self, value):
		self.hue = value

	def refresh(self):
		while True:
			pixels = [fromHSV(self.hue/360.0, random.uniform(0.9,1), .4) for i in range(0,16)]
			yield pixels



class Animator():
	def __init__(self, script=None, strip=None):
		self.script = script if script else DefaultScript()
		self.strip = strip if strip else _initNeoPixels()

	def changeScript(self, script):
		self.script = script

	def animate(self):
		print "Starting Animation"

		while True:
			pixels = self.script.refresh()

			for i in range(0,16):
				self.strip.setPixelColor(i, pixels[i])

			self.strip.show()
			time.sleep(20.0/1000.0)

	def run(self):
		thread = threading.Thread(target=self.animate, args=())
		thread.daemon = True                            # Daemonize thread
		thread.start()                                  # Start the execution

