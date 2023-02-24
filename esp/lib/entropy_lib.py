#
import random


def chaos(mpu, var):
    a = random.uniform(0, 2)
    b = temp_rand(mpu) % 4
    return int((a*var*(b-var))*1000)


def temp_rand(mpu):
    # vals = mpu.get_values()
    tmp=mpu.temperature
    return int(tmp * (10 ** 5)) % (10 ** 5)