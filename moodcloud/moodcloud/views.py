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
    if 'searchtext' in json_data['globals'][1]:
        result = models.Result(search_term=json_data['globals'][1]['searchtext'])
        result.save()
        for t in json_data['topics']:
            topic_mood = models.Emotion.objects.get(label=t[1]['mood'])
            topic = models.Topic(topic=t[0]['topictext'], mood=topic_mood)
            topic.save()
            result.topics.add(topic)
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

    # Then using that cookie, we call the AuthorizeCallback to get access to the search
    request = urllib2.Request(server_url+"/Home/AuthorizeCallback")
    request.add_header('Cookie', session_cookie)
    response = urllib2.urlopen(request)

    print "Calling search...",
    request = urllib2.Request(server_url+"/Home/MoodCloudSearchResult")
    request.add_header('Content-Type', 'application/json')
    request.add_header('Cookie', session_cookie)
    response2 = urllib2.urlopen(request, json.dumps({'search':search_term}))
    content = response2.read()
    print content

    if len(content) > 0:
        print "Fetching json result from api to verify...",
        request = urllib2.Request(server_url+"/api/moodcloud")
        response3 = urllib2.urlopen(request)
        data = response3.read()
        print data
        jd = json.loads(data)
        print jd
        if jd['topics'] is None:
            print "failed! (to get search results)"
            return None
        if jd['globals'][1]['searchtext'] == search_term:
            print "verified!"
        else:
            print "failed."
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
    return redirect('index')

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