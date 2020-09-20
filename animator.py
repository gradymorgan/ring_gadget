import time
import random
import threading
import colorsys
import math

from neopixel import *

import paho.mqtt.client as mqtt

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


class mqtt_connection:
	def __init__(self, host, port, topics = []):
		self.host = host
		self.port = port

		self.client = None
		self.current_subscriptions = topics

		self.on_update = None

	def subscribe(self, topics):
		if not self.client:
			return

		for topic in self.current_subscriptions:
			self.client.unsubscribe(topic)

		for topic in topics:
			self.client.subscribe(topic)

		self.current_subscriptions = topics

	# The callback for when the client receives a CONNACK response from the server.
	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code "+str(rc))

		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		for topic in self.current_subscriptions:
			print(topic)
			self.client.subscribe(topic)

	# The callback for when a PUBLISH message is received from the server.
	def on_message(self, client, userdata, msg):
		print(msg.topic, str(msg.payload), self.on_update)

		if self.on_update:
			self.on_update(float(msg.payload), msg.topic)

	def start(self):
		client = mqtt.Client("visuals")
		client.on_connect = self.on_connect
		client.on_message = self.on_message

		client.username_pw_set('mqtt', '')
		client.connect(self.host, self.port)

		self.client = client

		client.loop_start()



class DefaultScript():
	def __init__(self):
		pass

	def update(self):
		pass

	def refresh(self):
		return [Color(0,0,255)] * 16

class SingleBar():
	def __init__(self, maxValue, hue=189.0):
		self.hue = hue
		self.max = maxValue
		self.value = 0.0

	def update(self, value, key):
		print ("update", value)
		self.value = value

	def refresh(self):
		lit_pixels = math.ceil(self.value/self.max*16)
		c = fromHSV(self.hue/360.0, 1.0, self.value/self.max)
		
		l = [c]*lit_pixels + [Color(0,0,0)]*(16-lit_pixels)
		# print(self.value,self.max,lit_pixels, l)

		return l

class DoubleBar():
	def __init__(self, hue1, maxValue1, topic1, hue2, maxValue2, topic2):
		self.hue1 = hue1
		self.hue2 = hue2
		self.max1 = maxValue1
		self.max2 = maxValue2
		self.value1 = 0.0
		self.value2 = 0.0
		self.topic1 = topic1
		self.topic2 = topic2

	def update(self, value, key):
		if key == self.topic1:
			self.value1 = value
		if key == self.topic2:
			self.value2 = value

	def refresh(self):
		lit_pixels_1 = math.ceil(self.value1/self.max1*8)
		c_1 = fromHSV(self.hue1/360.0, 1.0, self.value1/self.max1)
		
		lit_pixels_2 = math.ceil(self.value2/self.max2*8)
		c_2 = fromHSV(self.hue2/360.0, 1.0, self.value2/self.max2)
		
		# print (lit_pixels_1, lit_pixels_2)

		l = [c_1]*lit_pixels_1 + [Color(0,0,0)]*(8-lit_pixels_1) + [Color(0,0,0)]*(8-lit_pixels_2) + [c_2]*lit_pixels_2
		# print(l)
		return l


class TwinkleScript():
	@staticmethod
	def interpColors(fromC, toC, percent):
		mid = (
			fromC[0] + (toC[0]-fromC[0])*percent,
			fromC[1] + (toC[1]-fromC[1])*percent,
			fromC[2] + (toC[2]-fromC[2])*percent
			)
		return mid

	@staticmethod
	def randomSaturation():
		(f,t) = (0.7,1)
		r = random.gauss(t, (t - f)/3.0)
		return max(0,min(1-abs(t-r), 1))

	@staticmethod
	def randomBrightness(average):
		return max(0,min(random.gauss(average,.1), 1))


	def __init__(self, hue=60):
		self.hue = hue
		self.brightness = .4

		self.STEPS = 10
		

	def update(self, value):
		self.hue = value

	def setBrightness(self, value):
		self.brightness = value
		
	def refresh(self):
		target_pixels_hsv = [(0,0,self.brightness)]*16

		while True:
			current_pixels = target_pixels_hsv
			target_pixels_hsv = [(self.hue/360.0, TwinkleScript.randomSaturation(), TwinkleScript.randomBrightness(self.brightness)) for i in range(0,16)]

			for step in range(0, self.STEPS):			
				pixels = [TwinkleScript.interpColors( current_pixels[i], target_pixels_hsv[i], step / float(self.STEPS)) for i in range(0,16)]
				yield [fromHSV(pix[0], pix[1], pix[2]) for pix in pixels]




class Animator():
	def __init__(self, script=None, strip=None):
		self.script = script if script else DefaultScript()
		self.strip = strip if strip else _initNeoPixels()

	def changeScript(self, script):
		self.script = script

	def animate(self):
		print("Starting Animation")

		while True:
			pixels = self.script.refresh()

			for i in range(0,16):
				self.strip.setPixelColor(i, pixels[i])

			self.strip.show()
			time.sleep(100.0/1000.0)

	def run(self):
		thread = threading.Thread(target=self.animate, args=())
		thread.daemon = True                            # Daemonize thread
		thread.start()                                  # Start the execution


mqtt_client = mqtt_connection('192.168.14.101', 1883, ['homeassistant/sensor/water_usage_today/state'])
mqtt_client.start()

animator = Animator(DefaultScript())
animator.run()

displays = [
	(['homeassistant/sensor/water_usage_today/state','homeassistant/sensor/energy_usage_today/state'], DoubleBar(217, 200, 'homeassistant/sensor/water_usage_today/state', 60, 20, 'homeassistant/sensor/energy_usage_today/state'), lambda v,k,s : s.update(v,k)),
	(['homeassistant/sensor/water_usage_today/state'], SingleBar(200, 217), lambda v,k,s : s.update(v,k) ),
	(['homeassistant/sensor/energy_usage_today/state'], SingleBar(20, 60), lambda v,k,s : s.update(v,k) )
]

def setDisplay(display):
	script = display[1]
	animator.changeScript(script)
	mqtt_client.on_update = lambda v,k : display[2](v,k,script)
	mqtt_client.subscribe(display[0])

i = 0
while True:
	i += 1
	setDisplay(displays[i%3])
	time.sleep(15)


