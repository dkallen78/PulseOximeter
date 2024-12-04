## Raspberry Pi Pico Pulse Oximeter

Before getting started make sure you search for and install the following libraries on your Pico:
* micropython_max30102 (https://github.com/n-elia/MAX30102-MicroPython-driver/tree/main)
* micropython_ssd1306 (https://github.com/stlehmann/micropython-ssd1306)

Next, download the pulse-oximeter.py file and upload it to your Pico

![Pulse oximeter schematic with Raspberry Pi Pico and ssd1306 OLED screen](https://github.com/dkallen78/PulseOximeter/blob/main/breadboard-i2c-2.jpg)

SpO2 is kind of janky but it works. 