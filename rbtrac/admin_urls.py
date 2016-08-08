from __future__ import unicode_literals

from django.conf.urls import patterns, url

from rbtrac.extension import TracExtension


urlpatterns = patterns(
    'rbtrac.views',

    url(r'^$', 'configure'),
)