from utime import sleep, sleep_ms, ticks_ms
from math import log
import utime as time
import json
import random
from machine import Pin, I2C
import network
#import mpu6050
from mpu6500 import MPU6500
import uasyncio
from web_server import Nanoweb
import ubinascii
import uhashlib
from wifi_connect import WiFiConnect
from entropy_lib import chaos, temp_rand

DEBUG = True

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
mpu = MPU6500(i2c)

naw = Nanoweb()
MAX_SIZE=4050


"""
def connect_wifi():
    if  not wlan.isconnected():
        wlan.active(True)
        print("wifi connect")
        wlan.connect("ssid","psw13")
        sleep(2)
        ipadd=wlan.ifconfig()[0]
        print("connected, init", ipadd)
"""
wlan = network.WLAN(network.STA_IF)

def connect_wifi():
    print("wifi connect")
    try:
        net = WiFiConnect(retries=20)
        wc = net.connect()
        ip_addr = net.ifconfig()[0]
        print("connected, init:",str(ip_addr))
    except:
        print("WiFiConnect.ERR")

     
connect_wifi()
#deactivate to save battery
wlan.active(False)

def get_uptime():
    uptime_s = int(time.ticks_ms() / 1000)
    uptime_h = int(uptime_s / 3600)
    uptime_m = int(uptime_s / 60)
    uptime_m = uptime_m % 60
    uptime_s = uptime_s % 60
    return ('{:02d}h {:02d}m {:02d}z'.format(uptime_h, uptime_m, uptime_s))

def random_shuffle(seq):
    l = len(seq)
    for i in range(l):
        j = random.randrange(l)
        seq[i], seq[j] = seq[j], seq[i]

# Read values from sensors
def get_data():
    gyro = mpu.gyro
    accel = mpu.acceleration
    if DEBUG:
        print(gyro[0],gyro[1],gyro[2], accel[0], accel[1], accel[2])
    
    ax=accel[0] #vals["AcX"]
    ay=accel[1] #vals["AcY"]
    az=accel[2] #vals["AcZ"]
    gx=gyro[0] #vals["GyX"]
    gy=gyro[1] #vals["GyY"]
    gz=gyro[2] #vals["GyZ"]
    return (ax, ay, az, gx, gy, gz)


def merge_data(data):
    # Random chaos to one input, hash together and extract random part
    r=int(random.uniform(0, 5))
    l=list(data)
    l[r]=chaos(mpu, l[r])
    data=tuple(l)
    sha256 = uhashlib.sha256()
    sha256.update(str(data).encode())
    h=ubinascii.hexlify(sha256.digest()).decode()
    v=temp_rand(mpu) % 9
    if v <= 4:
        r=int(random.uniform(47,62))
        return h[r:]
    else:
        r=int(random.uniform(2,27))
        return h[:r]

def add_entropy(entropy_str, data):
    entropy_str += merge_data(data)
    if len(entropy_str) > MAX_SIZE+20:
        str = list(entropy_str)
        r=int(random.uniform(1, 25))
        str = str[r:]
        random_shuffle(str)
        entropy_str=''.join(str)
    return entropy_str

def measure_entropy(entropy_str):
    # Using the shannon entropy formula to calculate the entropy
    shannon = 0
    for x in set(entropy_str):
        p_x = float(entropy_str.count(x))/len(entropy_str)
        shannon += - p_x*log(p_x, 2)
    return shannon

def rng():
    global entropy_str
    i=0
    if not "entropy_str" in globals():
        entropy_str = ""
        while True:
            sample_period = int(random.uniform(800, 4000))
            sleep_ms(sample_period)
            data = get_data()
            entropy_str = add_entropy(entropy_str, data)
            i+=1
            if i % 5 == 0:
                print("Current entropy: {} bits".format(measure_entropy(entropy_str)))
                print("Current lenght:", len(entropy_str))
            if len(entropy_str) > MAX_SIZE and measure_entropy(entropy_str) > 3.99:
                break
    else:
        for i in range(4):
            sample_period = int(random.uniform(100, 400))
            sleep_ms(sample_period)
            data = get_data()
            entropy_str = add_entropy(entropy_str, data)
        print("Current entropy: {} bits".format(measure_entropy(entropy_str)))
        print("Current lenght:", len(entropy_str))
    return entropy_str

rng()

#define and start web server
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

@naw.route("/hex")
def entropy(request):
    await request.write("HTTP/1.1 200 OK\r\n\r\n")
    random = rng()
    await request.write(json.dumps({
        "": random}))
    
@naw.route("/")
def entropy(request):
    await request.write("HTTP/1.1 200 OK\r\n\r\n")
    random = ubinascii.b2a_base64(rng())
    await request.write(json.dumps({
        "": random}))
    
loop = uasyncio.get_event_loop()
if DEBUG:
    print("web server - run")
loop.create_task(naw.run())
connect_wifi()
loop.run_forever()

