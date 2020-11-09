'''NeoPixel_UDP_Server LED layer, calling via UDP Calls.'''
'''Based on'''
'''https://github.com/scottlawsonbc/audio-reactive-led-strip'''
'''Builded up an own server'''
'''https://github.com/husky-koglhof/NeoPixel_UDP_Server'''

import logging
logger = logging.getLogger(__name__)

import platform
import os
import numpy as np
import socket

SOFTWARE_GAMMA_CORRECTION = False
"""Set to False because the firmware handles gamma correction + dither"""

"""Location of the gamma correction table"""
GAMMA_TABLE_PATH = os.path.join(os.path.dirname(__file__), 'gamma_table.npy')

class NeoPixelUDPServer:
    def __init__(self, count, server, brightness):
        '''Constructor'''
        self.pixels = [0 for i in range(count)]
        self.brightness = brightness
        self.server = server

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        """Gamma lookup table used for nonlinear brightness correction"""
        self._gamma = np.load(GAMMA_TABLE_PATH)

        # """Pixel values that were most recently displayed on the LED strip"""
        # self._prev_pixels = np.tile(253, (3, count))

        """Pixel values for the LED strip"""
        self._pixels = np.tile(1, (3, count))

        self._is_python_2 = int(platform.python_version_tuple()[0]) == 2

        # Turn all pixels off
        self._pixels *= 0

    def begin(self):
        pass

    def numPixels(self):
        return len(self.pixels)

    def setPixelColor(self, i, color):
        self.pixels[i] = color

    def getPixelColor(self, i):
        return self.pixels[i]

    def show(self):
        # Turn all pixels off
        self._pixels *= 0

        start = 0
        row = 1
        while start < len(self.pixels):
            end = start + len(self.pixels)

            # Build up the data
            p = 0
            for px in self.pixels[start:end]:
                [r, g, b] = self.getANSIPx(px)

                self._pixels[0, p] = r
                self._pixels[1, p] = g
                self._pixels[2, p] = b

                p = p+1

            start = end
            row += 1

            """Sends UDP packets to ESP32 to update LED strip values
            The ESP32 will receive and decode the packets to determine what values
            to display on the LED strip. The communication protocol supports LED strips
            with a maximum of 256 LEDs.
            The first element contains the brightness of the LED strip.
            After that the packet encoding scheme is:
                |i|r|g|b|
            where
                i (0 to 255): Index of LED to change (zero-based)
                r (0 to 255): Red value of LED
                g (0 to 255): Green value of LED
                b (0 to 255): Blue value of LED
            """
            # Truncate values and cast to integer
            self._pixels = np.clip(self._pixels, 0, 255).astype(int)
            # Optionally apply gamma correction
            p = self._gamma[self._pixels] 
            np.copy(self._pixels)
            MAX_PIXELS_PER_PACKET = 126
            # Pixel indices
            idx = range(self._pixels.shape[1])
            # idx = [i for i in idx if not np.array_equal(p[:, i], self._prev_pixels[:, i])]
            # print("----> 2: ")
            # print(idx)
            n_packets = len(idx) // MAX_PIXELS_PER_PACKET + 1
            idx = np.array_split(idx, n_packets)

            for packet_indices in idx:
                m = '' if self._is_python_2 else []
                m = chr(self.brightness) # Set correct brightness on each call
                for i in packet_indices:
                    if self._is_python_2:
                        m += chr(i) + chr(p[0][i]) + chr(p[1][i]) + chr(p[2][i])
                    else:
                        m.append(i)  # Index of pixel to change
                        m.append(p[0][i])  # Pixel red value
                        m.append(p[1][i])  # Pixel green value
                        m.append(p[2][i])  # Pixel blue value
                m = m if self._is_python_2 else bytes(m)
                address = self.server.split(":")

                self._sock.sendto(m, (address[0], int(address[1])))
            self._prev_pixels = np.copy(p)

    def setBrightness(self, brightness):
        self.brightness = brightness

    def getANSIPx(self, color):
        r = color >> 16 & 0xff
        g = color >> 8  & 0xff
        b = color & 0xff
        return [r, g, b]

def get_pixel_interface(config, brightness, *args, **kwargs):
    '''Returns the pixel interface.'''
    logger.info('LED: remote enabled via NeoPixelUDPServer')

    return NeoPixelUDPServer(config['LED_COUNT'], config.get('LED_SERVER'), brightness)
