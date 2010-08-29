from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.doc import documentation_view
from piston.authentication import HttpBasicAuthentication, OAuthAuthentication

import badges.api.handlers as handlers
import badges.api.utils as utils


def h(name, require_auth=True):
    """Build a handler and mark it CSRF exempt"""
    handler = getattr(handlers, '%sHandler' % name)
    #auth = require_auth and HttpBasicAuthentication(realm='Badger API') or None
    #auth = require_auth and OAuthAuthentication(realm='Badger API') or None
    auth = require_auth and utils.API_AUTHENTICATION or None
    resource = Resource(handler=handler, authentication=auth)
    resource.csrf_exempt = True
    return resource


urlpatterns = patterns('',

   url(r'^profiles/(?P<claimed_by__username>[^/]+)/awards/', 
       h('ProfileAward'),
       name='badges_api_profile_awards'),
   url(r'^profiles/(?P<username>[^/]+)/', 
       h('Profile'),
       name='badges_api_profile'),
   url(r'^profiles/', 
       h('Profile'),
       name='badges_api_profile_collection'),
   url(r'^badges/(?P<badge__slug>[^/]+)/awards/(?P<id>[^/]+)/', 
       h('BadgeAward'),
       name='badges_api_award'),
   url(r'^badges/(?P<badge__slug>[^/]+)/awards/', 
       h('BadgeAward'),
       name='badges_api_award_collection'),
   url(r'^badges/(?P<badge__slug>[^/]+)/nominations/(?P<id>[^/]+)/',  
       h('Nomination'),
       name='badges_api_nomination'),
   url(r'^badges/(?P<badge__slug>[^/]+)/nominations/', 
       h('Nomination'),
       name='badges_api_nomination_collection'),
   url(r'^badges/(?P<slug>[^/]+)/', 
       h('Badge'), 
       name='badges_api_badge'),
   url(r'^badges/', 
       h('Badge'), 
       name='badges_api_collection'),

   url(r'^docs/$', documentation_view, name='badges_api_docs'),
   url(r'^$', h('Index'), name='badges_api_index'),
)

# This seems ugly, but CSRF middleware butts in otherwise...

from piston.authentication import ( oauth_access_token, oauth_request_token, 
    oauth_user_auth )

oauth_request_token.csrf_exempt = True
oauth_user_auth.csrf_exempt = True
oauth_access_token.csrf_exempt = True

urlpatterns += patterns('',
    url(r'^oauth/request_token/$', oauth_request_token),
    url(r'^oauth/authorize/$', oauth_user_auth),
    url(r'^oauth/access_token/$', oauth_access_token),
)
