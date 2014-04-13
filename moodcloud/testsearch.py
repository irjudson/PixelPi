import sys
import urllib2
import json

server_url = "http://whooly.cloudapp.net/"
search_term = None
session_cookie = None

if len(sys.argv) < 2:
    print "What search term?"
    sys.exit(1)
else:
    search_term = sys.argv[1]

print "Searching for: %s" % search_term

print "Getting front door...",
response = urllib2.urlopen(server_url)
if 'Set-Cookie' in response.headers:
    session_cookie = response.headers['Set-Cookie']
    print "done!"
else:
    print "Could not retrieve cookie!"
    sys.exit(1)

print "Calling authorizecallback...",
request = urllib2.Request(server_url+"/Home/AuthorizeCallback")
request.add_header('Cookie', session_cookie)
response = urllib2.urlopen(request)
print "done!"

print "Calling search...",
request = urllib2.Request(server_url+"/Home/MoodCloudSearchResult")
request.add_header('Content-Type', 'application/json')
request.add_header('Cookie', session_cookie)
response2 = urllib2.urlopen(request, json.dumps({'search':search_term}))
content = response2.read()
print "done!"
print response2
print content

if len(content) > 0:
    print "Fetching json result from api to verify...",
    request = urllib2.Request(server_url+"/api/moodcloud")
    response2 = urllib2.urlopen(request)
    jd = json.loads(response2.read())
    print jd
    if jd['topics'] is None:
        print "failed! (to get search results)"
        sys.exit(1)
    if jd['globals'][1]['searchtext'] == search_term:
        print "verified!"
    else:
        print "failed."
