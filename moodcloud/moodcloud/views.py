# Create your views here.
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse

from django.conf import settings

import urllib2

def index(request):
    return render(request, 'index.html', RequestContext(request))

def get_data(request):
    data = urllib2.urlopen(settings.DATA_URL).read()
    return HttpResponse(data, mimetype='application/json')