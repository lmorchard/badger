"""Utilities for class-based views and more

see also: http://www.slideshare.net/simon/classbased-views-with-django
"""

from django.utils.http import urlquote
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, authenticate, REDIRECT_FIELD_NAME
from django.conf import settings
from django.conf.urls.defaults import patterns
from django.core import urlresolvers

REDIRECT_FIELD_NAME = "next"


class Router(object):

    def __init__(self, *urlpairs):
        self.urlpatterns = patterns('', *urlpairs)
        # for 1.0 compatibility we pass in None for urlconf_name and then
        # modify the _urlconf_module to make self hack as if its the module.
        self.resolver = urlresolvers.RegexURLResolver(r'^/', None)
        self.resolver._urlconf_module = self
    
    def handle(self, request, path_override=None):
        if path_override is not None:
            path = path_override
        else:
            path = request.path_info
        path = '/' + path # Or it doesn't work
        callback, callback_args, callback_kwargs = self.resolver.resolve(path)
        return callback(request, *callback_args, **callback_kwargs)
    
    def __call__(self, request, path_override=None):
        return self.handle(request, path_override)

class BaseView(object):

    base_template = ''

    def get_urlpatterns(self):
        # Default behaviour is to introspect self for do_* methods
        from django.conf.urls.defaults import url 
        urlpatterns = []
        for method in dir(self):
            if method.startswith('do_'):
                callback = getattr(self, method)
                name = method.replace('do_', '')
                urlname = self.urlname_pattern % name
                urlregex = getattr(callback, 'urlregex', '^%s/$' % name)
                urlpatterns.append(
                    url(urlregex, callback, name=urlname)
                )
        return urlpatterns
    
    def get_urls(self):
        # In Django 1.1 and later you can hook this in to your urlconf
        from django.conf.urls.defaults import patterns
        return patterns('', *self.get_urlpatterns())
    
    def urls(self):
        return self.get_urls()
    urls = property(urls)
    
    def __call__(self, request, rest_of_url=''):
        if not request.path.endswith('/'):
            return HttpResponseRedirect(request.path + '/')
        router = Router(*self.get_urlpatterns())
        return router(request, path_override = rest_of_url)

    def require_login(self, request):
        if request.user.is_authenticated():
            return True
        else:
            return HttpResponseRedirect('%s?%s=%s' % (
                settings.LOGIN_URL, REDIRECT_FIELD_NAME, 
                urlquote(request.get_full_path())
            ))

    def render(self, request, template, context=None):
        context = context or {}
        context['base_template'] = self.base_template
        return render_to_response(
            'socialconnect/%s' % template, context, 
            context_instance=RequestContext(request)
        )

        return TemplateResponse(request, template, context)
    
