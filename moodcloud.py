import argparse
import csv
import socket
import time
import urllib2
import json
import pygame
import random
import logging
from subprocess import * 
from PIL import Image
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

logger = logging.getLogger("moodcloud")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("/home/pi/moodcloud/output.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(fh)

STEPS = 16

# 3 bytes per pixel
PIXEL_SIZE = 3

"""
Hostility - Red (255.0.0)
Guilt - Orange (255.125.0)
Fear - Yellow (255.255.0)
Joviality - Green (0.255.0)
Serenity - Cyan (0.255.255)
Sadness - Blue (0.0.255)
Fatigue - Magenta (255.0.255)
"""

logger.debug("Initializing pygame.")
pygame.init()
logger.debug("Initializing pygame mixer.")
pygame.mixer.init()

logger.debug("Loading audio files.")
#Load audio files into Sound objects
fear_track = pygame.mixer.Sound('/home/pi/moodcloud/Fear.wav')
sadness_track = pygame.mixer.Sound('/home/pi/moodcloud/Sadness.wav')
joviality_track = pygame.mixer.Sound('/home/pi/moodcloud/Joviality.wav')
fatigue_track = pygame.mixer.Sound('/home/pi/moodcloud/Fatigue.wav')
hostility_track = pygame.mixer.Sound('/home/pi/moodcloud/Hostility.wav')
serenity_track = pygame.mixer.Sound('/home/pi/moodcloud/Serenity.wav')
guilty_track = pygame.mixer.Sound('/home/pi/moodcloud/Guilt.wav')


EMOTIONS = {
    'Hostility' : hostility_track,
    'Guilt' : guilty_track,
    'Fear' : fear_track,
    'Joviality' : joviality_track,
    'Serenity' : serenity_track,
    'Sadness' : sadness_track,
    'Fatigue' : fatigue_track
}

RED = bytearray(b'\xff\x00\x00')
ORANGE = bytearray(b'\xff\xa5\x00')
YELLOW = bytearray(b'\xff\xff\x00')
GREEN = bytearray(b'\x00\x80\x00')
BLUE = bytearray(b'\x00\x00\xff')
VIOLET = bytearray(b'\xee\x82\xee')
RAINBOW = [RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET]
BLACK = bytearray(b'\x00\x00\x00')
WHITE = bytearray(b'\xff\xff\xff')



def write_stream(pixels):
    """
    """
    spidev.write(pixels)
    return


def correct_pixel_brightness(pixel):
    """
    """
    corrected_pixel = bytearray(3)
    corrected_pixel[0] = int(pixel[0] / 1.1)
    corrected_pixel[1] = int(pixel[1] / 1.1)
    corrected_pixel[2] = int(pixel[2] / 1.3)
    return corrected_pixel


def pixelinvaders():
    """
    """    
    logger.debug("Start PixelInvaders listener " + args.UDP_IP + ":" + str(args.UDP_PORT))
    sock = socket.socket(socket.AF_INET,  # Internet
                      socket.SOCK_DGRAM)  # UDP
    sock.bind((args.UDP_IP, args.UDP_PORT))
    UDP_BUFFER_SIZE = 1024
    while True:
        data, addr = sock.recvfrom(UDP_BUFFER_SIZE)  # blocking call
        pixels_in_buffer = len(data) / PIXEL_SIZE
        pixels = bytearray(pixels_in_buffer * PIXEL_SIZE)
        for pixel_index in range(pixels_in_buffer):
            pixel_to_adjust = bytearray(data[(pixel_index * PIXEL_SIZE):((pixel_index * PIXEL_SIZE) + PIXEL_SIZE)])
            pixel_to_filter = correct_pixel_brightness(pixel_to_adjust)
            pixels[((pixel_index) * PIXEL_SIZE):] = filter_pixel(pixel_to_filter[:], 1)
        write_stream(pixels)
        spidev.flush()

def strip():
    """
    """
    img = Image.open(args.filename).convert("RGB")
    input_image = img.load()
    image_width = img.size[0]
    logger.debug("%dx%d pixels" % img.size)
    # Create bytearray for the entire image
    # R, G, B byte per pixel, plus extra '0' byte at end for latch.
    logger.debug("Allocating...")
    column = [0 for x in range(image_width)]
    for x in range(image_width):
        column[x] = bytearray(args.array_height * PIXEL_SIZE + 1)

    logger.debug("Process Image...")
    for x in range(image_width):
        for y in range(args.array_height):
            value = input_image[x, y]
            y3 = y * 3
            column[x][y3] = value[0]
            column[x][y3 + 1] = value[1]
            column[x][y3 + 2] = value[2]

    logger.debug("Displaying...")
    while True:
        for x in range(image_width):
            write_stream(column[x])
            spidev.flush()
            time.sleep(0.001)
        time.sleep((args.refresh_rate / 1000.0))


def array():
    """
    """
    images = []
    if ('filelist.txt' in args.filename):
        with open(args.filename, 'r') as file:
            for filename in file:
                filename = filename.rstrip()
                if not filename:
                    continue
                logger.debug(filename)
                images.append(Image.open(filename).convert("RGB"))
    else:
        images.append(Image.open(args.filename).convert("RGB"))

    for img in images:
        input_image = img.load()
        logger.debug("%dx%d pixels" % img.size)
        logger.debug("Reading in array map")
        pixel_map_csv = csv.reader(open("pixel_map.csv", "rb"))
        pixel_map = []
        for p in pixel_map_csv:
            pixel_map.append(p)
        if len(pixel_map) != args.array_width * args.array_height:
            logger.debug("Map size error")
        logger.debug("Remapping")
        value = bytearray(PIXEL_SIZE)

        # Create a byte array ordered according to the pixel map file
        pixel_output = bytearray(args.array_width * args.array_height * PIXEL_SIZE + 1)
        for array_index in range(len(pixel_map)):
            value = bytearray(input_image[int(pixel_map[array_index][0]), int(pixel_map[array_index][1])])

        pixel_output[(array_index * PIXEL_SIZE):] = filter_pixel(value[:], 1)
        logger.debug("Displaying...")
        write_stream(pixel_output)
        spidev.flush()
        time.sleep((args.refresh_rate) / 1000.0)


def pan():
    """
    """
    img = Image.open(args.filename).convert("RGB")
    input_image = img.load()
    image_width = img.size[0]
    logger.debug("%dx%d pixels" % img.size)
    logger.debug("Reading in array map")
    pixel_map_csv = csv.reader(open("pixel_map.csv", "rb"))
    pixel_map = []
    for p in pixel_map_csv:
        pixel_map.append(p)
    if len(pixel_map) != args.array_width * args.array_height:
        logger.debug("Map size error")
    logger.debug("Remapping")

    # Create a byte array ordered according to the pixel map file
    pixel_output = bytearray(args.array_width * args.array_height * PIXEL_SIZE + 1)
    while True:
        for x_offset in range(image_width - args.array_width):
            for array_index in range(len(pixel_map)):
                value = bytearray(input_image[int(int(pixel_map[array_index][0]) + x_offset), int(pixel_map[array_index][1])])
                pixel_output[(array_index * PIXEL_SIZE):] = filter_pixel(value[:], 1)

        logger.debug("Displaying...")
        write_stream(pixel_output)
        spidev.flush()
        time.sleep((args.refresh_rate) / 1000.0)


def all_off():
    """
    """
    pixel_output = bytearray(args.num_leds * PIXEL_SIZE + 3)
    logger.debug("Turning all LEDs Off")
    for led in range(args.num_leds):
        pixel_output[led * PIXEL_SIZE:] = filter_pixel(BLACK, 1)
    write_stream(pixel_output)
    spidev.flush()


def all_on():
    """
    """
    pixel_output = bytearray(args.num_leds * PIXEL_SIZE + 3)
    logger.debug("Turning all LEDs On")
    for led in range(args.num_leds):
        pixel_output[led * PIXEL_SIZE:] = filter_pixel(WHITE, 1)
    write_stream(pixel_output)
    spidev.flush()


def fade():
    """
    """
    pixel_output = bytearray(args.num_leds * PIXEL_SIZE + 3)
    current_color = bytearray(PIXEL_SIZE)
    logger.debug("Displaying...")

    while True:
        for color in RAINBOW:
            for brightness in [x * 0.01 for x in range(0, 100)]:
                current_color[:] = filter_pixel(color[:], brightness)
                for pixel_offset in [(x * 3) for x in range(args.num_leds)]:
                    pixel_output[pixel_offset:] = current_color[:]
                write_stream(pixel_output)
                spidev.flush()
                time.sleep((args.refresh_rate) / 1000.0)
            for brightness in [x * 0.01 for x in range(100, 0, -1)]:
                current_color[:] = filter_pixel(color[:], brightness)
                for pixel_offset in [(x * 3) for x in range(args.num_leds)]:
                    pixel_output[pixel_offset:] = current_color[:]
                write_stream(pixel_output)
                spidev.flush()
                time.sleep(16)


def chase():
    """
    """
    pixel_output = bytearray(args.num_leds * PIXEL_SIZE + 3)
    logger.debug("Displaying...")
    current_color = bytearray(PIXEL_SIZE)
    pixel_index = 0
    while True:
        for current_color[:] in RAINBOW:
            for pixel_index in range(args.num_leds):
                pixel_output[((pixel_index - 2) * PIXEL_SIZE):] = filter_pixel(current_color[:], 0.2)
                pixel_output[((pixel_index - 1) * PIXEL_SIZE):] = filter_pixel(current_color[:], 0.4)
                pixel_output[((pixel_index) * PIXEL_SIZE):] = filter_pixel(current_color[:], 1)
                pixel_output += '\x00' * ((args.num_leds - 1 - pixel_index) * PIXEL_SIZE)

                write_stream(pixel_output)
                spidev.flush()
                time.sleep((args.refresh_rate) / 1000.0)
                pixel_output[((pixel_index - 2) * PIXEL_SIZE):] = filter_pixel(current_color[:], 0)


gamma = bytearray(256)


# Apply Gamma Correction and RGB / GRB reordering
# Optionally perform brightness adjustment
def filter_pixel(input_pixel, brightness):
    """
    """
    output_pixel = bytearray(PIXEL_SIZE)

    input_pixel[0] = int(brightness * input_pixel[0])
    input_pixel[1] = int(brightness * input_pixel[1])
    input_pixel[2] = int(brightness * input_pixel[2])

    output_pixel[0] = gamma[input_pixel[0]]
    output_pixel[1] = gamma[input_pixel[1]]
    output_pixel[2] = gamma[input_pixel[2]]
    return output_pixel

def server():
    """
    """
    lcd = Adafruit_CharLCDPlate()
    lcd.clear()
    lcd.message("MoodCloud v1.0!")
    time.sleep(1)

    btn = ((lcd.LEFT, 'Left.', lcd.ON),
            (lcd.RIGHT, 'Right.', lcd.ON),
            (lcd.UP, 'Up.', lcd.ON),
            (lcd.DOWN, 'Down.', lcd.ON),
            (lcd.SELECT, 'Select.', lcd.ON))

    cmd = "ip addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1"

    logger.debug("Connecting to server at: %s:%d" % (args.server, args.port))
    pixel_output = bytearray(args.num_leds * PIXEL_SIZE)
    while True:
        serverpath = "http://%s:%d/api/moodcloud" % (args.server, args.port)
        logger.debug("Grabbing next set of sentiment data from %s." % serverpath)
        data = json.loads(urllib2.urlopen(serverpath).read())
        logger.debug("Data: ")
        logger.debug(json.dumps(data))
        #logger.debug(json.dumps(data, sort_keys=True, indent=2))
        proc = Popen(cmd, shell=True, stdout=PIPE)
        ip = proc.communicate()[0]
        lcd.clear()
        lcd.message('IP %s' % (ip))
        logger.debug("Playing sounds...")
        moods = dict()
        if "topics" in data and data['topics'] is not None:
            for topic in data["topics"]:
                for element in topic:
                    if "mood" in element:
                        mood = element["mood"]
                        if mood in moods.keys():
                            moods[mood] += 1
                        else:
                            moods[mood] = 1
            MAX_VOLUME = 0.95
            MIN_VOLUME = 0.25
            maxm = max(moods.values())
            minm = min(moods.values())
            logger.debug("Freq: Max %d Min %d" % (maxm, minm))
            scale = 1.0 - (maxm - minm) / (MAX_VOLUME - MIN_VOLUME)
            translate = maxm - MAX_VOLUME
            logger.debug("Scale: %f Translate: %f" % (scale, translate))
            for mood in moods:
                moods[mood] = moods[mood] / float(maxm)
                logger.debug("Setting %s to volume %f" % (mood, moods[mood]))
            for emotion, track in EMOTIONS.items():
                track.set_volume(0.0)
                if emotion in moods:
                    track.set_volume(moods[mood])
                else:
                    logger.debug("Leaving sounds another round.")

        logger.debug("Displaying...")
        if 'pixels' in data and data['pixels'] is not None:
            pixels = data['pixels']
            for led in range(args.num_leds):
                current_color = bytearray(chr(pixels[led][0]) + chr(pixels[led][1]) + chr(pixels[led][2]))
                pixel_output[led * PIXEL_SIZE:] = filter_pixel(current_color, 0.9)
            write_stream(pixel_output)
            spidev.flush()
            time.sleep(16)
        else:
            logger.debug("Leaving lights another round.")
            time.sleep(16)


parser = argparse.ArgumentParser(add_help=True, version='1.0', prog='pixelpi.py')
subparsers = parser.add_subparsers(help='sub command help?')
common_parser = argparse.ArgumentParser(add_help=False)
common_parser.add_argument('--chip', action='store', dest='chip_type', default='WS2801', choices=['WS2801'], help='Specify chip type WS2801')
common_parser.add_argument('--verbose', action='store_true', dest='verbose', default=True, help='enable verbose mode')
common_parser.add_argument('--spi_dev', action='store', dest='spi_dev_name', required=False, default='/dev/spidev0.0', help='Set the SPI device descriptor')
common_parser.add_argument('--refresh_rate', action='store', dest='refresh_rate', required=False, default=1000, type=int, help='Set the refresh rate in ms (default 1000ms)')
parser_strip = subparsers.add_parser('strip', parents=[common_parser], help='Stip Mode - Display an image using POV and a LED strip')
parser_strip.set_defaults(func=strip)
parser_strip.add_argument('--filename', action='store', dest='filename', required=False, help='Specify the image file eg: hello.png')
parser_strip.add_argument('--array_height', action='store', dest='array_height', required=True, type=int, default='7', help='Set the Y dimension of your pixel array (height)')
parser_array = subparsers.add_parser('array', parents=[common_parser], help='Array Mode - Display an image on a pixel array')
parser_array.set_defaults(func=array)
parser_array.add_argument('--filename', action='store', dest='filename', required=False, help='Specify the image file eg: hello.png')
parser_array.add_argument('--array_width', action='store', dest='array_width', required=True, type=int, default='7', help='Set the X dimension of your pixel array (width)')
parser_array.add_argument('--array_height', action='store', dest='array_height', required=True, type=int, default='7', help='Set the Y dimension of your pixel array (height)')
parser_pixelinvaders = subparsers.add_parser('pixelinvaders', parents=[common_parser], help='Pixelinvaders Mode - setup pixelpi as a Pixelinvaders slave')
parser_pixelinvaders.set_defaults(func=pixelinvaders)
parser_pixelinvaders.add_argument('--udp-ip', action='store', dest='UDP_IP', required=True, help='Used for PixelInvaders mode, listening address')
parser_pixelinvaders.add_argument('--udp-port', action='store', dest='UDP_PORT', required=True, default=6803, type=int, help='Used for PixelInvaders mode, listening port')
parser_fade = subparsers.add_parser('fade', parents=[common_parser], help='Fade Mode - Fade colors on all LEDs')
parser_fade.set_defaults(func=fade)
parser_fade.add_argument('--num_leds', action='store', dest='num_leds', required=True, default=50, type=int,  help='Set the  number of LEDs in the string')
parser_chase = subparsers.add_parser('chase', parents=[common_parser], help='Chase Mode - Chase display test mode')
parser_chase.set_defaults(func=chase)
parser_chase.add_argument('--num_leds', action='store', dest='num_leds', required=True, default=50, type=int,  help='Set the  number of LEDs in the string')
parser_pan = subparsers.add_parser('pan', parents=[common_parser], help='Pan Mode - Pan an image across an array')
parser_pan.set_defaults(func=pan)
parser_pan.add_argument('--filename', action='store', dest='filename', required=False, help='Specify the image file eg: hello.png')
parser_pan.add_argument('--array_width', action='store', dest='array_width', required=True, type=int, default='7', help='Set the X dimension of your pixel array (width)')
parser_pan.add_argument('--array_height', action='store', dest='array_height', required=True, type=int, default='7', help='Set the Y dimension of your pixel array (height)')
parser_all_on = subparsers.add_parser('all_on', parents=[common_parser], help='All On Mode - Turn all LEDs On')
parser_all_on.set_defaults(func=all_on)
parser_all_on.add_argument('--num_leds', action='store', dest='num_leds', required=True, default=50, type=int,  help='Set the  number of LEDs in the string')
parser_all_off = subparsers.add_parser('all_off', parents=[common_parser], help='All Off Mode - Turn all LEDs Off')
parser_all_off.set_defaults(func=all_off)
parser_all_off.add_argument('--num_leds', action='store', dest='num_leds', required=True, default=50, type=int,  help='Set the  number of LEDs in the string')
server_parser = subparsers.add_parser('server', parents=[common_parser], help='Connect to a server for data')
server_parser.set_defaults(func=server)
server_parser.add_argument('--host', action='store', dest='server', default='whooly.cloudapp.net', help='Connect to a specific server')
server_parser.add_argument('--port', action='store', dest='port', default=80, type=int, help='Connect to a specific server port')
server_parser.add_argument('--num_leds', action='store', dest='num_leds', default=96, type=int,  help='Set the  number of LEDs in the string')

args = parser.parse_args()

spidev = file(args.spi_dev_name, "wb")

for i in range(256):
    gamma[i] = int(pow(float(i) / 255.0, 2.5) * 255.0)



#Play Sound objects in infinite loop
fear_track.play(-1)
sadness_track.play(-1)
joviality_track.play(-1)
fatigue_track.play(-1)
hostility_track.play(-1)
serenity_track.play(-1)
guilty_track.play(-1)

#Set all tracks to volume 0
fear_track.set_volume(0.0)
sadness_track.set_volume(0.0)
joviality_track.set_volume(0.0)
fatigue_track.set_volume(0.0)
hostility_track.set_volume(0.0)
serenity_track.set_volume(0.0)
guilty_track.set_volume(0.0)

args.func()
