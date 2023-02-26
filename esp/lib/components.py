# HW components for catro.py - RGB LED and gyro
from machine import Pin, I2C
from mpu6500 import MPU6500
from neopixel import NeoPixel


DEBUG = False


#------------------ RGB LED --------------------
class StatusLed(NeoPixel):
    _last_state = (0,0,0)

    def show_led(self, color, force=False):
        if self._last_state == color and not force:
            return

        self.fill(color)
        self.write()
        self._last_state = color


def init_rgb_led():
    print("[init_rgb_led]")
    return StatusLed(Pin(8), 1)
    

#------------------ gyro --------------------
def init_gyro():
    print("[init_gyro]")
    i2c = I2C(0, sda=Pin(0), scl=Pin(1))
    return MPU6500(i2c)


# Read values from sensors
def get_data(mpu):
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
