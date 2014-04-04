# Create your views here.
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.core import serializers
from django.utils.timezone import utc
from django.conf import settings

import urllib2
import json
import datetime

import pytz
import models

def make_result_from_json(json_data):
    print "Making result from data"
    print json_data
    if 'searchtext' in json_data['globals'][1]:
        result = models.Result(search_term=json_data['globals'][1]['searchtext'])
        print "Made base result"
        result.save()
        for t in json_data['topics']:
            print "Working on topics"
            topic_mood = models.Emotion.objects.get(label=t[1]['mood'])
            print "Got mood for topic"
            topic = models.Topic(topic=t[0]['topictext'], mood=topic_mood)
            print "Made topic"
            topic.save()
            result.topics.add(topic)
            print "Added topic to result"
        result.save()
        return result
    else:
        print "Didn't find searchtext in globals"
        return None

def fetch():
    result = make_result_from_json(json.loads(urllib2.urlopen(settings.DATA_URL).read()))
    return result

def do_search(search_term):
    server_url = "http://whooly.cloudapp.net/"
    session_cookie = None

    # First we have to retrieve the cookie by GET'ing the whooly home page
    response = urllib2.urlopen(server_url)
    if 'Set-Cookie' in response.headers:
        session_cookie = response.headers['Set-Cookie']
    else:
        return None

    print "Got cookie"

    # Then using that cookie, we call the AuthorizeCallback to get access to the search
    request = urllib2.Request(server_url+"/Home/AuthorizeCallback")
    request.add_header('Cookie', session_cookie)
    response = urllib2.urlopen(request)

    print "Got authorized"

    # Finally we run the search with the term passed in
    request = urllib2.Request(server_url+"/Home/MoodCloudSearchResult")
    request.add_header('Content-Type', 'application/json')
    request.add_header('Cookie', session_cookie)
    response = urllib2.urlopen(request, json.dumps({'search':search_term}))
    content = response.read()

    print "Called search"
    print content

    # And as a post step we create a result from the json data
    if len(content) > 0:
        request = urllib2.Request(server_url+"/api/moodcloud")
        data = urllib2.urlopen(request).read()
        print data
        result = make_result_from_json(json.loads(data))
        print "Search Result: ", result
        return result

    print "No response from API?"

def index(request):
    context = RequestContext(request)
    context['IP'] = models.Address.load().network or "Unknown"
    context['IP_updated'] = models.Address.load().last_updated or "Never updated"
    return render(request, 'index.html', context)

@csrf_exempt
def search(request, search_term):
    result = do_search(search_term)
    if result is not None:
        print "Worked"
    else:
        print "Failed"

# Get data from Whoooly
def fetch_data(request):
    # Get Data
    fetch()
    # Store the data in a model
    return HttpResponse()

# Return data to app/device
def get_data(request):
    result = None
    try:
        diff =  pytz.utc.localize( datetime.datetime.utcnow() ) - models.Result.objects.latest().created_at
        if models.Result.objects.count() == 0:
            result = fetch()
        if diff.seconds > settings.UPDATE_FREQUENCY:
            result = fetch()
        if result == None:
            result = models.Result.objects.latest()
        json_data = serializers.serialize('json', [result])
        jd = json.loads(json_data)[0]
        jd['fields']['topics'] = json.loads(serializers.serialize('json', result.topics.all()))
        moods = dict()
        count = 0
        for topic in result.topics.all():
            jmd = json.loads(serializers.serialize('json', [topic.mood]))[0]
            jd['fields']['topics'][count]['fields']['mood'] = jmd
            count += 1
    except Exception as e:
        print "Exception: %s" % e.message
        jd = {}
    return HttpResponse(json.dumps(jd), mimetype='application/json')

@csrf_exempt
def register(request):
    resp = HttpResponse("Ok")
    if request.POST:
        data = request.body.decode(encoding='UTF-8')
        jsondata = json.loads(data)
        addr = models.Address(network=jsondata['ip'])
        addr.save()
    return resp