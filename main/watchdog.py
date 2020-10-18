# picoweb test

print ("starting picoweb test")

import network
import json

import picoweb
import ubinascii

import ure as re

from machine import Pin, RTC, Timer
import time
import utime


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
        with open('pw/main/config/config.json') as cf:
                config = json.load(cf)
	max_time = int(float(config['config']['maxtime']) * 60)
	un = config['config']['un']
	pw = config['config']['pw']
	name = config['config']['name']

except Exception:
	print("not on ota")

else:
	try:
        	with open('config/config.json') as cf:
                	config = json.load(cf)
		max_time = int(float(config['config']['maxtime']) * 60)

	except Exception:
		pass


# connect to wifi
def do_connect(SSID, Pass):
	import network
	print("connecting to: ", SSID)
	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)
	wlan.config(dhcp_hostname='wd')
	if not wlan.isconnected():
		print('connecting to network...')
		wlan.connect(SSID, Pass)
		while not wlan.isconnected():
			pass
	print('network config:', wlan.ifconfig())


try:
        with open('config/wifi_cfg.json') as cf:
                wifi_cfg = json.load(cf)
        print ("SSID: ", wifi_cfg['wifi']['ssid'])
        print ("PW: ", wifi_cfg['wifi']['password'])

except Exception:
                pass

do_connect(wifi_cfg['wifi']['ssid'], wifi_cfg['wifi']['password'])


rtc = RTC()
# synchronize with ntp
# need to be connected to wifi


print ("Getting ntp time")
import ntptime

tries = 10
for i in range(tries):
        try:
		ntptime.settime(server="au.pool.ntp.org") # set the rtc datetime from the remote server
		rtc.datetime()    # get the date and time in UTC
		print("Sync ntp")
        except:
                if i < tries - 1: # i is zero indexed
			print(".")
			time.sleep_ms(10000)
			continue
        break


watchdog_time_1 = utime.time()
watchdog_time_2 = utime.time()
ntp_time = watchdog_time_1



# check watchdog times
def check_watchdogs(timer):
	global watchdog_time_1
	global watchdog_time_2
	global max_time

	print ("current time = ")
	print (utime.time())
	print ("watchdog 1 time + max time = ")
	print (watchdog_time_1 + max_time)

	if ( utime.time() > watchdog_time_1 + max_time ):
		res(1)
		print ("Watchdog restart 1")
		watchdog_time_1 = utime.time()

	print ("current time = ")
	print (utime.time())
	print ("watchdog 2 time + max time = ")
	print (watchdog_time_2 + max_time)

	if ( utime.time() > watchdog_time_2 + max_time ):
		res(2)
		print ("Watchdog restart 2")
		watchdog_time_2 = utime.time()

#	resetHWWatchdog()


# create an interupt timer to check the watchdog times
print("create timer")
timer = Timer(0)


# reset freetronics hardware watchdog attached to gpio 5

HWWPin = Pin(5, Pin.OUT)

def resetHWWatchdog():
	global HWWPin

	print ("Reset Watchdog Watchdog")

	HWWPin.on()
	time.sleep_ms(20)
	HWWPin.off()


# check if rtc needs updating from ntp after 30 minutes (1800 seconds)  (not currently used)
'''
def resetntp(t):
	global ntp_time
	if (t > ntp_time + 1800):
		ntp_time = t
		return True
	return False
'''


# timer interupt every 60 seconds to check watchdog times

timer.init(period=60000, mode=Timer.PERIODIC, callback=check_watchdogs)


def require_auth(func):

	def auth(req, resp):
		auth = req.headers.get(b"Authorization")
		if not auth:
			yield from resp.awrite(
				'HTTP/1.0 401 NA\r\n'
				'WWW-Authenticate: Basic realm="Picoweb Realm"\r\n'
				'\r\n'
			)
			return

		auth = auth.split(None, 1)[1]
		auth = ubinascii.a2b_base64(auth).decode()
		req.username, req.passwd = auth.split(":", 1)
		yield from func(req, resp)

	return auth


def turn_on(relay):
	if (relay == 1):
		relay_1.on()
		led.on()
		time.sleep(1)
		relay_1.off()
		led.off()
	elif (relay == 2):
		relay_2.on()
		led.on()
		time.sleep(1)
		relay_2.off()
		led.off()

def turn_off(relay):
	if (relay == 1):
		relay_1.on()
		led.on()
		time.sleep(15)
		relay_1.off()
		led.off()
	elif (relay == 2):
		relay_2.on()
		led.on()
		time.sleep(15)
		relay_2.off()
		led.off()

def res(relay):
	if (relay == 1):
		turn_off(1)
		time.sleep(1)
		turn_on(1)
	elif (relay == 2):
		turn_off(2)
		time.sleep(1)
		turn_on(2)


def watchdog_1():
	global watchdog_time_1
	print("Watchdog 1 fed")
	resetHWWatchdog()
	watchdog_time_1 = utime.time()


def watchdog_2():
	global watchdog_time_2
	print("Watchdog 2 fed")
	resetHWWatchdog()
	watchdog_time_2 = utime.time()




#
# This is a picoweb example showing a web page route
# specification using view decorators (Flask style).
#
import picoweb

print ("import picoweb")

app = picoweb.WebApp(__name__)

print ("set up routes")

@app.route("/")
def index(req, resp):

	t = utime.localtime(watchdog_time_1)
#	print('t1 =', t)
	wd_time_1 = '{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}:{:02d} UTC'.format(t[0], t[1], t[2], t[3], t[4], t[5], t[6])
	t = utime.localtime(watchdog_time_2)
#	print('t2 =', t)
	wd_time_2 = '{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}:{:02d} UTC'.format(t[0], t[1], t[2], t[3], t[4], t[5], t[6])
	t = utime.localtime(ntp_time)
#	print('t1 =', t)
	ntp_t = '{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}:{:02d} UTC'.format(t[0], t[1], t[2], t[3], t[4], t[5], t[6])

	data = {"ntp": ntp_t, "wd1": wd_time_1, "wd2": wd_time_2, "name": name}

	yield from picoweb.start_response(resp)
	yield from app.render_template(resp, "watchdog.tpl", (data,))


@app.route("/squares")
def squares(req, resp):
	yield from picoweb.start_response(resp)
	yield from app.render_template(resp, "squares.tpl", (req,))


@app.route("/authority")
@require_auth
def index(req, resp):

	if (req.username == un) and (req.passwd == pw):
		yield from picoweb.start_response(resp)
		yield from resp.awrite("You logged in with username: %s, password: %s" % (req.username, req.passwd))
		print("un: ", un)
		print("pw: ", pw)

	else:
# redirect to "/"
		headers = {"Location": "/authority"}
		yield from picoweb.start_response(resp, status="401", headers=headers)





# styles.css file send
@app.route(re.compile('^\/(.+\.css)$'))
def styles(req, resp):
	file_path = req.url_match.group(1)
	headers = b"Cache-Control: max-age=86400\r\n"
#	if b"gzip" in req.headers.get(b"Accept-Encoding", b""):
#		file_path += ".gz"
#		headers += b"Content-Encoding: gzip\r\n"
#	print("sending " + file_path)
	yield from app.sendfile(resp, "static/" + file_path, "text/css", headers)

# on response
@app.route(re.compile('^\/(on_.+)$'))
def on(req, resp):
	file_path = req.url_match.group(1)

	print("File path: ", file_path)
	if (file_path == 'on_1'):
		turn_on(1)
	elif (file_path == 'on_2'):
		turn_on(2)
# redirect to "/"
	headers = {"Location": "/"}
	yield from picoweb.start_response(resp, status="303", headers=headers)


# off response
@app.route(re.compile('^\/(off_.+)$'))
def off(req, resp):
	file_path = req.url_match.group(1)

	print("File path: ", file_path)
	if (file_path == 'off_1'):
		turn_off(1)
	elif (file_path == 'off_2'):
		turn_off(2)
# redirect to "/"
	headers = {"Location": "/"}
	yield from picoweb.start_response(resp, status="303", headers=headers)


# restart response
@app.route(re.compile('^\/(restart_.+)$'))
def restart(req, resp):
	file_path = req.url_match.group(1)

	print("File path: ", file_path)
	if (file_path == 'restart_1'):
		res(1)
	elif (file_path == 'restart_2'):
		res(2)
# redirect to "/"
	headers = {"Location": "/"}
	yield from picoweb.start_response(resp, status="303", headers=headers)


@app.route("/watchdog_1")
def wd1(req, resp):
	watchdog_1()
	yield from picoweb.start_response(resp)
	yield from resp.awrite("Ok")

@app.route("/watchdog_2")
def wd2(req, resp):
	watchdog_2()
	yield from picoweb.start_response(resp)
	yield from resp.awrite("Ok")




try:
	print("run app")

	import ulogging as logging
	logging.basicConfig(level=logging.INFO)

	app.run(debug=True, host="10.0.0.23", port=80)


except KeyboardInterrupt:
	timer.deinit()
	print('Caught Control-C')


