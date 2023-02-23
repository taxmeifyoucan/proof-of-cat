import network
from time import sleep

# Wifi name and password

SSID=name
PASS=password

def connect_wifi():
    if  not wlan.isconnected():
        wlan.active(True)
        print("Connecting wifi")
        wlan.connect(SSID,PASS)
        sleep(2)
        ipadd=wlan.ifconfig()[0]
        print("Wifi connected, IP address of the device", ipadd)
        print("If the above value doesn't seem correct, run the program again")

connect_wifi()