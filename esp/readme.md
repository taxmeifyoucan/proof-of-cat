# Catropy software (WIP)

ESP32 is collecting data from gyro and acceloremeter, creates arrays of collected coordinates and calculates how much entropy was collected. When it reaches 256 bits, data are extracted using chaos function and served as API or saved to file.

Right now, everything is implemented using micropython but c++ usage to better utilize ESP features is researched. 

Python [libraries and functions](https://octopusengine.org/download/micropython/stable.tar) are developed together with hardware by [Ocotpus Engine](octopusengine.org).

The webserver used in this project [Nanoweb](https://github.com/hugokernel/micropython-nanoweb). 
