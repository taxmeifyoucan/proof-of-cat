# Catropy docs

This reasearch was conducted as a contribution to [Ethereum KZG Ceremony](https://github.com/ethereum/kzg-ceremony). To participate in the ceremony, CRNG under the name _Catropy_ was built. 

Catropy, originally proposed in the Proof-of-Cat CatPaper, is a small device dedicated to harvesting entropy from cats. Current design is a result of various iterations and consists of a custom board with:
- ESP32 C3 with wifi, bluetooth, USB-C 
- Sensors for gathering data - gyroscope, accelerometer
- Lipo battery 500-800mAh and charging circuit 

![image](./src/assets/catropy_front.png) 
![image](./src/assets/catropy_back.png) 
![image](./src/assets/catropy_scheme.png)


The software is written in micropython and serves a simple API over local network to provide the randomness. More documentation and code improvements are coming soon, current version can be [found here](https://github.com/taxmeifyoucan/proof-of-cat/tree/master/esp). 