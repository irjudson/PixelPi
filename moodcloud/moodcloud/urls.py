from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'moodcloud.views.home', name='home'),
    url(r'^data/', 'moodcloud.views.get_data', name='data'),
    url(r'^fetchdata/', 'moodcloud.views.fetch_data', name='data'),
    url(r'^register', 'moodcloud.views.register', name='register'),
    url(r'^search/(?P<search_term>)$', 'moodcloud.views.search', name='search'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
