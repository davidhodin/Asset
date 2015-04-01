#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'michelin.views.home', name='home'),
    # url(r'^michelin/', include('michelin.foo.urls')),
    # url(r'^test/$', include('Catalog.urls')),
	
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	url(r'^sam/', include('SAM.urls')),
    url(r'^connexion/$', 'michelin.views.connexion', name='connexion'),
    url(r'^deconnexion/$', 'michelin.views.deconnexion', name='deconnexion'),
	url(r'^$', 'michelin.views.start'),
)
