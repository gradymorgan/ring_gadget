import time
import random
import colorsys
import threading

from neopixel import *
from flask import Flask

app = Flask(__name__)

def initNeoPixels():
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

current_hue = 0
def animate():
	print "Starting Animation"
	strip = initNeoPixels()

	while True:
		for i in range(0,16):
			color = fromHSV(current_hue/360.0, random.uniform(0.9,1), .4)
			strip.setPixelColor(i, color)

		strip.show()
		time.sleep(100.0/1000.0)


def fromHSV(hue, saturation, value):
	(r,g,b) = [int(255*i) for i in colorsys.hsv_to_rgb(hue, saturation, value)]
	return Color(r,g,b)

def startAnimation():
	thread = threading.Thread(target=animate, args=())
	thread.daemon = True                            # Daemonize thread
	thread.start()                                  # Start the execution



@app.route("/hue/<hue>")
def setHue(hue):
	global current_hue
	current_hue = float(hue)
	return hue

@app.route("/hue")
def getHue():
	return current_hue


startAnimation()

if __name__ == "__main__":
	app.run()
