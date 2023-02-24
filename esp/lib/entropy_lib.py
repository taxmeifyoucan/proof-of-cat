# entropy_lib for proofof.cat | catro.py
# mpu: MPU6500 6-axis motion tracking device

import random
import ubinascii
import uhashlib
from math import log


MAX_SIZE = 4050 # 4050
TARGET_ENTROPY = 3.99 # 3.99

def chaos(mpu, var):
    a = random.uniform(0, 2)
    b = temp_rand(mpu) % 4
    return int((a*var*(b-var))*1000)


def temp_rand(mpu):
    tmp=mpu.temperature
    return int(tmp * (10 ** 5)) % (10 ** 5)


def random_shuffle(seq):
    l = len(seq)
    for i in range(l):
        j = random.randrange(l)
        seq[i], seq[j] = seq[j], seq[i]
    return seq


def add_entropy(mpu, entropy_str, data):
    entropy_str += merge_data(mpu, data)
    if len(entropy_str) > MAX_SIZE+20:
        str = list(entropy_str)
        r=int(random.uniform(1, 25))
        str = str[r:]
        str = random_shuffle(str)
        entropy_str=''.join(str)
    return entropy_str


def merge_data(mpu, data):
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


def measure_entropy(entropy_str):
    # Using the shannon entropy formula to calculate the entropy
    shannon = 0
    for x in set(entropy_str):
        p_x = float(entropy_str.count(x))/len(entropy_str)
        shannon += - p_x*log(p_x, 2)
    return shannon


def hexor(str1, str2):
    # XOR two hex strings
    xor = ""
    for i in range(min(len(str1), len(str2))):
        res = hex(int(str1[i], 16) ^ int(str2[i], 16))[2:]
        if len(res) < len(str1[i]):
            res = "0"*(len(str1[i])-len(res))
        xor += res
    return xor
