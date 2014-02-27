#!/usr/bin/env bash
#

# Ensure audio is loaded
modprobe snd-bcm2835

# Set the audio out
amixer cset numid=3 1

# Play a test sound
aplay /usr/share/sounds/alsa/Noise.wav

sleep 10

# Start moodcloud
python /home/pi/moodcloud/moodcloud.py server &
