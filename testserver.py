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

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        color = next_color()
        data = {
            'global-color' : (next_color(), next_color(), next_color(), random.choice(range(75,100))/100.0),
        }
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
