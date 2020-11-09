'''WLED LED layer, calling via API Calls.'''
'''https://github.com/Aircoookie/WLED/wiki/JSON-API'''

import logging
logger = logging.getLogger(__name__)
import requests

class WLEDPixel:
    def __init__(self, count, server, brightness, rows=1):
        '''Constructor'''
        self.pixels = [0 for i in range(count)]
        self.width = count//rows
        self.brightness = brightness
        self.server = server

    def begin(self):
        pass

    def numPixels(self):
        return len(self.pixels)

    def setPixelColor(self, i, color):
        self.pixels[i] = color

    def getPixelColor(self, i):
        return self.pixels[i]

    def show(self):
        start = 0
        row = 1
        task = {"seg":{"bri": self.brightness, "i":[]}}
        while start < len(self.pixels):
            end = start + self.width

            # Build up the data
            p = 0
            for px in self.pixels[start:end]:
                task['seg']['i'].append(p)
                p = p+1
                task['seg']['i'].append(p)
                task['seg']['i'].append(self.getANSIPx(px))

            start = end
            row += 1
        # Now call it
        # e.g.
        # curl --header "Content-Type: application/json" --request POST --data '{"seg":{"i":[0,6,[0,0,0], 6,12,[0,0,0], 12,18,[0,0,0], 18,24,[0,0,0], 24,31,[0,0,0]]}}' http://192.168.1.15/json/state
        # task = {"seg":{"i":[0,6,[0,0,0], 6,12,[0,0,0], 12,18,[0,0,0], 18,24,[0,0,0], 24,31,[0,0,0]]}}
        # print(task)
        try:
            resp = requests.post('http://' + self.server + '/json/state', json=task)
            if resp.status_code != 200:
                raise ApiError('POST /json/state/ {}'.format(resp.text))
        except Exception as e:
            logger.error(str(e))

    def setBrightness(self, brightness):
        logger.info("--> Actual Brightness: " + str(brightness))
        self.brightness = brightness

    def getANSIPx(self, color):
        r = color >> 16 & 0xff
        g = color >> 8  & 0xff
        b = color & 0xff
        return [r, g, b]

def get_pixel_interface(config, brightness, *args, **kwargs):
    '''Returns the pixel interface.'''
    logger.info('LED: locally enabled via WLEDPixel')
    return WLEDPixel(config['LED_COUNT'], config.get('LED_SERVER'), brightness, config.get('LED_ROWS', 1))
