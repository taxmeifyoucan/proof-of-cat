# hooka2 - deploy0 2022/09

from time import sleep

import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
sleep(5)
# wlan.connect('ssid', 'password')
print("wifi connect")

sleep(5)
print("upip: micropython-octopuslab-installer")
import upip
upip.install('micropython-octopuslab-installer')

sleep(5)
print("deploy: .../download/micropython/hooka22.tar")
from lib import octopuslab_installer
deplUrl = "https://octopusengine.org/download/micropython/stable.tar"
octopuslab_installer.deploy(deplUrl)
