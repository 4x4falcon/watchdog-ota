# -------------------------------------------------------------------------------

try:
	import usocket as socket
except:
	import socket

from machine import Pin, RTC, Timer
import network
import time
import utime
import json

from .functions import *

esp32 = True
# select esp32 or esp8266
from os import uname
if (uname().sysname == 'esp8266'):
	esp32 = False
	print ("found esp8266")


ledstate = 0
led = Pin(2, Pin.OUT)

if (esp32):
	relay_1 = Pin(22, Pin.OUT)
	relay_2 = Pin(21, Pin.OUT)
else:
	relay_1 = Pin(5, Pin.OUT)
	relay_2 = Pin(4, Pin.OUT)

# maximum time that can elapse before watchdog resets the attached device
# 5 minutes = 5 * 60s
max_time = 5 * 60

try:
        with open('watchdog/main/config/config.json') as cf:
                config = json.load(cf)

except Exception:
	print("not on ota")

else:
	try:
        	with open('config/config.json') as cf:
                	config = json.load(cf)
	except Exception:
		pass

max_time = int(float(config['config']['maxtime']) * 60)



rtc = RTC()
# synchronize with ntp
# need to be connected to wifi

# load wifi config
wifi_cfg = None
try:
	with open('config/wifi_cfg.json') as cf:
		wifi_cfg = json.load(cf)
	print ("SSID: ", wifi_cfg['wifi']['ssid'])
	print ("PW: ", wifi_cfg['wifi']['password'])

except Exception:
	print ("No file")
	pass


# connect to wifi
do_connect(wifi_cfg['wifi']['ssid'], wifi_cfg['wifi']['password'])

import ntptime

tries = 10
for i in range(tries):
        try:
                ntptime.settime() # set the rtc datetime from the remote server
                rtc.datetime()    # get the date and time in UTC
        except:
                if i < tries - 1: # i is zero indexed
                        sleep_ms(10000)
                        continue
        break

# create an interupt timer to check the watchdog times

timer = Timer(0)

watchdog_time_1 = utime.time()
watchdog_time_2 = utime.time()
ntp_time = watchdog_time_1


def web_page():

	global watchdog_time_1
	global watchdog_time_2
	global ntp_time

	t = utime.localtime(watchdog_time_1)
#	print('t1 =', t)
	wd_time_1 = '{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}:{:02d} UTC'.format(t[0], t[1], t[2], t[3], t[4], t[5], t[6])
	t = utime.localtime(watchdog_time_2)
#	print('t2 =', t)
	wd_time_2 = '{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}:{:02d} UTC'.format(t[0], t[1], t[2], t[3], t[4], t[5], t[6])
	t = utime.localtime(ntp_time)
#	print('t1 =', t)
	ntp_t = '{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}:{:02d} UTC'.format(t[0], t[1], t[2], t[3], t[4], t[5], t[6])


	html = """<html><head> <title>The Internet Host Watchdog Timer</title> <meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="icon" href="data:,">
	<style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
	h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}
	.button{display: inline-block; background-color: #e7bd3b; border: none; border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
	.button2{background-color: #4286f4;}
	.button3{background-color: #ff0000;}
	</style></head>

	<body> <h1>The Internet Host Watchdog Timer</h1>

	<p>Started at """ + ntp_t + """</p>

	<p>Watchdog 1 reset at """ + wd_time_1 + """</p>
	<p><a href="/?led=on1"><button class="button">Turn ON 1</button></a></p>
	<p><a href="/?led=off1"><button class="button button2">Turn OFF 1</button></a></p>
	<p><a href="/?led=restart1"><button class="button button3">Restart 1</button></a></p>

	<p>Watchdog 2 reset at """ + wd_time_2 + """</p>
	<p><a href="/?led=on2"><button class="button">Turn ON 2</button></a></p>
	<p><a href="/?led=off2"><button class="button button2">Turn OFF 2</button></a></p>
	<p><a href="/?led=restart2"><button class="button button3">Restart 2</button></a></p>
	<p></p>
	<p><a href="/">Reload</a></p>
	</body></html>"""
	return html

def restart_1():
	global watchdog_time_1
	relay_1.on()
	led.on()
	time.sleep(15)
	relay_1.off()
	led.off()
	time.sleep(10)
	relay_1.on()
	led.on()
	time.sleep(1)
	relay_1.off()
	led.off()
	ledstate = 0
	watchdog_time_1 = utime.time()

def restart_2():
	global watchdog_time_2
	relay_2.on()
	led.on()
	time.sleep(15)
	relay_2.off()
	led.off()
	time.sleep(10)
	relay_2.on()
	led.on()
	time.sleep(1)
	relay_2.off()
	led.off()
	ledstate = 0
	watchdog_time_2 = utime.time()

def turn_on_1():
	relay_1.on()
	led.on()
	time.sleep(1)
	relay_1.off()
	led.off()

def turn_off_1():
	relay_1.on()
	led.on()
	time.sleep(15)
	relay_1.off()
	led.off()


def turn_on_2():
	relay_2.on()
	led.on()
	time.sleep(1)
	relay_2.off()
	led.off()

def turn_off_2():
	relay_2.on()
	led.on()
	time.sleep(15)
	relay_2.off()
	led.off()

def watchdog_1():
	global watchdog_time_1
	print("Watchdog 1 fed")
	watchdog_time_1 = utime.time()

def watchdog_2():
	global watchdog_time_2
	print("Watchdog 2 fed")
	watchdog_time_2 = utime.time()


def check_watchdogs(timer):
	global watchdog_time_1
	global watchdog_time_2
	global max_time

	if ( utime.time() > watchdog_time_1 + max_time ):
		restart_1()
		print ("Watchdog restart 1")

	print ("current time = ")
	print (utime.time())
	print ("watchdog 2 time + max time = ")
	print (watchdog_time_2 + max_time)

	if ( utime.time() > watchdog_time_2 + max_time ):
		restart_2()
		print ("Watchdog restart 2")

# reset freetronics hardware watchdog attached to gpio 5
HWWPin = Pin(5, Pin.OUT)

def resetHWWatchdog():
	global HWWPin

	print ("Reset Watchdog Watchdog")

	HWWPin.on()
	time.sleep_ms(20)
	HWWPin.off()


# check if rtc needs updating from ntp after 30 minutes (1800 seconds)  (not currently used)
def resetntp(t):
	global ntp_time
	if (t > ntp_time + 1800):
		ntp_time = t
		return True
	return False



# timer interupt every 60 seconds to check watchdog times
timer.init(period=60000, mode=Timer.PERIODIC, callback=check_watchdogs)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

try:
	while True:
# reset the hardware watchdog for this device
		resetHWWatchdog()

		conn, addr = s.accept()
		print('Got a connection from %s' % str(addr))
		request = conn.recv(1024)
		request = str(request)

		led_on1 = request.find('/?led=on1')
		led_off1 = request.find('/?led=off1')
		led_on2 = request.find('/?led=on2')
		led_off2 = request.find('/?led=off2')
		led_restart1 = request.find('/?led=restart1')
		led_restart2 = request.find('/?led=restart2')
		led_watchdog1 = request.find('/?led=watchdog1')
		led_watchdog2 = request.find('/?led=watchdog2')

		if led_on1 == 6:
			turn_on_1()
		if led_off1 == 6:
			turn_off_1()
		if led_restart1 == 6:
			restart_1()
		if led_watchdog1 == 6:
			watchdog_1()

		if led_on2 == 6:
			turn_on_2()
		if led_off2 == 6:
			turn_off_2()
		if led_restart2 == 6:
			restart_2()
		if led_watchdog2 == 6:
			watchdog_2()

		response = web_page()
		conn.send('HTTP/1.1 200 OK\n')
		conn.send('Content-Type: text/html\n')
		conn.send('Connection: close\n\n')
		conn.sendall(response)
		conn.close()

except KeyboardInterrupt:
	timer.deinit()
	print('Caught Control-C')

