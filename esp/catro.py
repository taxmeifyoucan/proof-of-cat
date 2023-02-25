from utime import sleep, sleep_ms, ticks_ms
import utime as time
import json
import random
from machine import Pin, I2C
import network
import uasyncio
import ubinascii
from web_server import Nanoweb
from mpu6500 import MPU6500
from neopixel import NeoPixel
from wifi_connect import WiFiConnect
from entropy_lib import MAX_SIZE, TARGET_ENTROPY, add_entropy, measure_entropy
from sys import exit

DEBUG = False

print(f"MAX_SIZE: {MAX_SIZE}")
print(f"TARGET_ENTROPY: {TARGET_ENTROPY}")
print("-"*30)


class StatusLed(NeoPixel):
    _last_state = (0,0,0)

    def show_led(self, color, force=False):
        if self._last_state == color and not force:
            return

        self.fill(color)
        self.write()
        self._last_state = color
        

print("Starting Catropy")

led = StatusLed(Pin(8), 1)

for i in range(10):
    led.show_led((200,0,0))
    sleep_ms(100)
    led.show_led((0,200,0))
    sleep_ms(100)



i2c = I2C(0, sda=Pin(0), scl=Pin(1))
mpu = MPU6500(i2c)
naw = Nanoweb()
wlan = network.WLAN(network.STA_IF)

def connect_wifi():
    if not wlan.isconnected():
        print("Connecting wifi")
        try:
            net = WiFiConnect(retries=20)
            wc = net.connect()
            sleep(2)
            ip_addr = net.ifconfig()[0]
            if ip_addr == "0.0.0.0":
                led.show_led((200,0,0))
                print("The wifi doesn't seem not be connected corretly, please check your settings and run the program again.")
            else:
                print("IP address:",ip_addr)
                led.show_led((0,200,0))
        except:
            print("The wifi did not connect, please check your settings and run the program again.")
            led.show_led((200,0,0))
     
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


# Read values from sensors
def get_data():
    gyro = mpu.gyro
    accel = mpu.acceleration
    if DEBUG:
        print(gyro[0],gyro[1],gyro[2], accel[0], accel[1], accel[2])
    else:
        print(".",end="")
    
    ax=accel[0] #vals["AcX"]
    ay=accel[1] #vals["AcY"]
    az=accel[2] #vals["AcZ"]
    gx=gyro[0] #vals["GyX"]
    gy=gyro[1] #vals["GyY"]
    gz=gyro[2] #vals["GyZ"]
    return (ax, ay, az, gx, gy, gz)


def rng():
    global entropy_str
    led.show_led((0,200,0))
    i=0
    if not "entropy_str" in globals():
        entropy_str = ""
        while True:
            sample_period = int(random.uniform(500, 1100)) 
            sleep_ms(sample_period)
            data = get_data()
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
            data = get_data()
            entropy_str = add_entropy(mpu, entropy_str, data)
        print("Current entropy: {} bits".format(measure_entropy(entropy_str)))
        print("Current lenght:", len(entropy_str))
    led.show_led((0,0,200))
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
    await request.write("HTTP/1.1 200 OK\r\n\r\n")
    random = ubinascii.b2a_base64(rng())
    await request.write(json.dumps({
        "": random}))
    
loop = uasyncio.get_event_loop()
if DEBUG:
    print("Starting webserver")

loop.create_task(naw.run())
connect_wifi()
if not wlan.isconnected():
    exit()
led.show_led((0,0,200))
loop.run_forever()

