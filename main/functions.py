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


