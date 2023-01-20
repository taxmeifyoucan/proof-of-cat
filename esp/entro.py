from utime import sleep, sleep_ms, ticks_ms
from math import log
import utime as time
import json
import random
from machine import Pin, SoftI2C
import network
import mpu6050
import uasyncio
from ws import Nanoweb
import ubinascii
import uhashlib

wlan = network.WLAN(network.STA_IF)
i2c = SoftI2C(scl=Pin(1), sda=Pin(0))     #initializing the I2C method for ESP32
mpu = mpu6050.accel(i2c)
naw = Nanoweb()
MAX_SIZE=4500

def connect_wifi():
    if  not wlan.isconnected():
        wlan.active(True)
        print("wifi connect")
        wlan.connect("ssid","psswd")
        sleep(2)
        ipadd=wlan.ifconfig()[0]
        print("connected, init", ipadd)

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

def chaos(var):
    a = random.uniform(0, 2)
    b = temp_rand() % 4
    return int((a*var*(b-var))*1000)

# XOR two hex strings
def hexor(str1, str2):
    xor = ""
    for i in range(min(len(str1), len(str2))):
        res = hex(int(str1[i], 16) ^ int(str2[i], 16))[2:]
        if len(res) < len(str1[i]):
            res = "0"*(len(str1[i])-len(res))
        xor += res
    return xor

# Read values from sensors
def get_data():
    vals = mpu.get_values()
    ax=vals["AcX"]
    ay=vals["AcY"]
    az=vals["AcZ"]
    gx=vals["GyX"]
    gy=vals["GyY"]
    gz=vals["GyZ"]
    return (ax, ay, az, gx, gy, gz)

def temp_rand():
    vals = mpu.get_values()
    tmp=(vals["Tmp"])
    return int(tmp * (10 ** 5)) % (10 ** 5)

def merge_data(data):
    # Random chaos to one input, hash together and extract random part
    r=int(random.uniform(0, 5))
    l=list(data)
    l[r]=chaos(l[r])
    data=tuple(l)
    sha256 = uhashlib.sha256()
    sha256.update(str(data).encode())
    h=ubinascii.hexlify(sha256.digest()).decode()
    v=temp_rand() % 9
    if v <= 4:
        r=int(random.uniform(40,62))
        return h[r:]
    else:
        r=int(random.uniform(3,45))
        return h[:r]

def add_entropy(entropy_str, data):
    entropy_str += merge_data(data)
    if len(entropy_str) > MAX_SIZE+20:
        str = list(entropy_str)
        r=int(random.uniform(19, 50))
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
            sample_period = int(random.uniform(200, 900))
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
        for i in range(5):
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

@naw.route("/")
def entropy(request):
    await request.write("HTTP/1.1 200 OK\r\n\r\n")
    random = ubinascii.b2a_base64(rng())
    await request.write(json.dumps({
        "": random}))
    
loop = uasyncio.get_event_loop()
loop.create_task(naw.run())
connect_wifi()
loop.run_forever()


