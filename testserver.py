#!/usr/bin/env python
#
import sys
import datetime
import BaseHTTPServer
import SimpleHTTPServer
import json

def next_color():
    return datetime.datetime.now().microsecond % 255

# Fear
# Sadness
# Joviality
# Fatigue
# Hostility
# Serenity
# Guilty
# Positivity

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        color = next_color()
        data = dict()
        data["ContentEncoding"] = None
        data["ContentType"] = None
        data["Data"] = {
            "globals" : [
                        { "color" : [] },
                        { "searchtext" : "" },
                        { "topicsCount" : 0 }
                    ],
                    "topics" : [
                        [
                            { "topictext" : "" },
                            { "mood" : "" },
                            { "hexColor" : "" }
                        ]
                    ],
                    "pixels" : [
                        [0, 255, 0, 0.5], 
                        ...
                    ]
        }
        data["JsonRequestBehavior"] = 0
        data["MaxJsonLength"] = None
        data["RecursionLimit"] = None

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

print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()