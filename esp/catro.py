from utime import sleep, sleep_ms, ticks_ms
import utime as time
from sys import exit
import json
import random
import network
import uasyncio
import ubinascii
from wifi_connect import WiFiConnect
from web_server import Nanoweb
from entropy_lib import MAX_SIZE, TARGET_ENTROPY, add_entropy, measure_entropy
from components import init_rgb_led, init_gyro, get_data



DEBUG = False
LED_INTENSITY = 128

print(f"MAX_SIZE: {MAX_SIZE}")
print(f"TARGET_ENTROPY: {TARGET_ENTROPY}")
print("-"*30)

print("Starting Catropy")


led = init_rgb_led()

for i in range(10):
    led.show_led((LED_INTENSITY,0,0))
    sleep_ms(100)
    led.show_led((0,LED_INTENSITY,0))
    sleep_ms(100)

mpu = init_gyro()
naw = Nanoweb()
wlan = network.WLAN(network.STA_IF)


def connect_wifi():
    if not wlan.isconnected():
        print("Connecting wifi")
        try:
            led.show_led((LED_INTENSITY,LED_INTENSITY,0))
            net = WiFiConnect(retries=100)
            wc = net.connect()

            ip_addr = net.ifconfig()[0]
            if ip_addr == "0.0.0.0":
                led.show_led((LED_INTENSITY,0,0))
                print("The wifi doesn't seem not be connected corretly, please check your settings and run the program again.")
            else:
                print("IP address:",ip_addr)
                led.show_led((0,LED_INTENSITY,0))
        except:
            print("The wifi did not connect, please check your settings and run the program again.")
            led.show_led((LED_INTENSITY,0,0))
     
connect_wifi()
if not wlan.isconnected():
    exit()


#deactivate to save battery
#wlan.active(False)

def get_uptime():
    uptime_s = int(time.ticks_ms() / 1000)
    uptime_h = int(uptime_s / 3600)
    uptime_m = int(uptime_s / 60)
    uptime_m = uptime_m % 60
    uptime_s = uptime_s % 60
    return ('{:02d}h {:02d}m {:02d}z'.format(uptime_h, uptime_m, uptime_s))


def rng():
    global entropy_str
    led.show_led((0,LED_INTENSITY,0))
    i=0
    if not "entropy_str" in globals():
        entropy_str = ""
        while True:
            sample_period = int(random.uniform(500, 1100)) 
            sleep_ms(sample_period)
            data = get_data(mpu)
            entropy_str = add_entropy(mpu, entropy_str, data)
            i+=1
            if i % 5 == 0:
                print("Current entropy: {} bits".format(measure_entropy(entropy_str)))
                print("Current lenght:", len(entropy_str))
            if len(entropy_str) > MAX_SIZE and measure_entropy(entropy_str) > TARGET_ENTROPY:
                break
    else:
        for i in range(4):
            sample_period = int(random.uniform(100, 400))
            sleep_ms(sample_period)
            data = get_data(mpu)
            entropy_str = add_entropy(mpu, entropy_str, data)
        print("Current entropy: {} bits".format(measure_entropy(entropy_str)))
        print("Current lenght:", len(entropy_str))
    led.show_led((0,0,LED_INTENSITY))
    return entropy_str

print("Starting randomness generation")
rng()
print("Initial entropy gathered, starting API")

@naw.route("/status")
async def status(request):
    await request.write("HTTP/1.1 200 OK\r\n")
    await request.write("Content-Type: application/json\r\n\r\n")
    uptime_str = get_uptime()
    shannon=measure_entropy(entropy_str)
    bits = len(entropy_str) * 4
    await request.write(json.dumps({
        "uptime": uptime_str,
        "Shannon entropy": shannon,
        "lenght": bits}))

@naw.route("/")
def entropy(request):
    await request.write("HTTP/1.1 200 OK\r\n")
    await request.write("Content-Type: application/json\r\n\r\n")
    random = ubinascii.b2a_base64(rng())[:-2]
    await request.write(json.dumps({
        "": random}))
    
loop = uasyncio.get_event_loop()
if DEBUG:
    print("Starting webserver")

loop.create_task(naw.run())
connect_wifi()
if not wlan.isconnected():
    exit()
led.show_led((0,0,LED_INTENSITY))
loop.run_forever()
