#!/usr/bin/env python
import urllib2
import json

data = json.loads(urllib2.urlopen("http://whooly.cloudapp.net/api/moodcloud").read())
print data