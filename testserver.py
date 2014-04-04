#!/usr/bin/env python
#
import sys
import datetime
import BaseHTTPServer
import SimpleHTTPServer
import random
import json

def next_color():
    return datetime.datetime.now().microsecond % 255

"""
Hostility - Red (255.0.0)
Guilt - Orange (255.125.0)
Fear - Yellow (255.255.0)
Joviality - Green (0.255.0)
Serenity - Cyan (0.255.255)
Sadness - Blue (0.0.255)
Fatigue - Magenta (255.0.255)
"""

EMOTIONS = [ "Fear", "Sadness", "Joviality", "Fatigue", "Hostility", "Serenity", "Guilt" ]

# Fear
# Sadness
# Joviality
# Fatigue
# Hostility
# Serenity
# Guilty

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        pixels = list()
        for i in range(100):
            pixels.append((next_color(), next_color(), next_color(), 1.0))
        color = next_color()

        data = dict()
        data["ContentEncoding"] = None
        data["ContentType"] = None
        data["Data"] = {
            "globals" : [
                        { "color" : [next_color(), next_color(), next_color(), 1.0] },
                        { "searchtext" : "" },
                        { "topicsCount" : 0 }
                    ],
             "topics" : list(),
             "pixels" : pixels
            }

        data["JsonRequestBehavior"] = 0
        data["MaxJsonLength"] = None
        data["RecursionLimit"] = None
    
    topics = data["Data"]["topics"]

    for i in range(16):
            topic = list()
        topic.append({ "topictext" : "foo" })
        topic.append({ "mood" : random.choice(EMOTIONS) })
        topic.append({ "hexColor" : "#00FF00" })
        topics.append(topic)

        json_data = json.dumps(data)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-length", len(json_data))
        self.end_headers()
        self.wfile.write(json_data)

host = '127.0.0.1'

if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8000

httpd = BaseHTTPServer.HTTPServer((host, port), MyHandler) 

sa = httpd.socket.getsockname()

print("Serving HTTP on", sa[0], "port", sa[1], "...")
httpd.serve_forever()
