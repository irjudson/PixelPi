#!/usr/bin/env bash
#

# Run every minute to make sure the moodcloud is running.

PID="`ps auwx | grep moodcloud.py | grep -v grep`"

if [ "x${PID}" == "x" ]; then
	echo "Moodcloud not running, restarting."
	/home/pi/moodcloud/startup.sh
	exit 0
else
	echo "Moodcloud running, exiting."
fi

exit 0
