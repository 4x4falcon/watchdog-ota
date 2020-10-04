rf = 0
ws = 0
ntpset = 0
bright = 0


# toggle function
def toggle(p):
        p.value(not p.value())

# get battery voltage function
def getBatteryVoltage(batteryvoltage):
	import machine
	adc = machine.ADC(0)
	raw = adc.read()
	return raw/1024 * batteryvoltage

# isr for template counter
# template interrupt callback
def template_cb(d):
        global rf
        rf += 1
#       print("Switch toggled", rf)

# check if rtc needs updating from ntp after 30 minutes (1800 seconds)
def resetntp(t):
	global ntpset
	if (t > ntpset + 1800):
		ntpset = t
		return True
	return False

# reset freetronics hardware watchdog attached to gpio 5
#from machine import Pin
#from time import sleep_ms
#HWWPin = Pin(8, Pin.OUT)

#def resetHWWatchdog():
#	global HWWPin

#	print ("Reset Hardware Watchdog")

#	HWWPin.high()
#	sleep_ms(20)
#	HWWPin.low()


# connect wifi
def do_connect(SSID, Pass):
	import network
	print("connecting to: ", SSID)
	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)
	if not wlan.isconnected():
		print('connecting to network...')
		wlan.connect(SSID, Pass)
		while not wlan.isconnected():
			pass
	print('network config:', wlan.ifconfig())


