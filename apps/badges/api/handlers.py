"""
Badger API
"""
from datetime import datetime

import piston

from piston.handler import BaseHandler, AnonymousBaseHandler, typemapper
from piston.utils import rc, require_mime, require_extended
from piston.emitters import Emitter

from oauth import oauth

from django.utils import simplejson as json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify

from avatar.models import avatar_file_path
from avatar.templatetags.avatar_tags import avatar_url

from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from badges import BADGE_DEFAULT_SIZE
from badges.models import ( Badge, BadgeNomination, BadgeAward, 
        BadgeAwardee, badge_file_path )

import badges.api.hacks # Ensure piston gets monkeypatched

AVATAR_DEFAULT_SIZE = 80


def site_url(path):
    #return path
    if path.startswith('http'): return path
    return 'http://%s%s' % (Site.objects.get_current().domain, path)

def request_token_ready(request, token):
    error = request.GET.get('error', '')
    ctx = RequestContext(request, { 'error': error, 'token': token})
    return render_to_response('piston/request_token_ready.html',
                          context_instance = ctx)

def render_created(self, request, new_obj, new_url):
    """Quick hack to return a 201 Created along with a JSON rendering of 
    what was created"""
    resp = rc.CREATED
    emitter, ct = Emitter.get('json')
    resp['Content-Type'] = ct
    resp['Location'] = new_url
    srl = emitter(new_obj, typemapper, self, self.fields, False)
    resp.content = srl.render(request)
    return resp


class IndexHandler(BaseHandler):
    """Index entry point, offers links to docs and major collections"""
    
    anonymous = 'AnonymousIndexHandler'
    allowed_methods = ('GET',)

    def read(self, request):
        """Since we have a user, add profile links to response"""
        links_to_build = {
            'badges': 'badges_api_collection',
            'profiles': 'badges_api_profile_collection',
            'docs': 'badges_api_docs',
        }
        links = dict( 
            (n[0], site_url(reverse(n[1])))
            for n in links_to_build.items() 
        )
        if request.user.is_authenticated():
            links['authenticated'] = {
                'text/html': site_url(request.user.get_absolute_url()),
                'application/json': site_url(reverse('badges_api_profile', 
                    kwargs={'username': request.user.username}))
            }
        return links


class AnonymousIndexHandler(IndexHandler, AnonymousBaseHandler):
    pass


class ProfileHandler(BaseHandler):
    model = User
    anonymous = 'AnonymousProfileHandler'
    fields = ( 'username', 'image', 'links', )

    @classmethod
    def resource_uri(handler, obj=None):
        return ('badges_api_profile', [ '%s' % obj, ])

    @classmethod
    def image(handler, user):
        return { 
            'href': site_url(avatar_url(user, AVATAR_DEFAULT_SIZE)),
            'width': AVATAR_DEFAULT_SIZE, 'height': AVATAR_DEFAULT_SIZE,
        }

    @classmethod
    def links(handler, user):
        return {
            'self': {
                'text/html': site_url(user.get_absolute_url()),
                'application/json': site_url(reverse('badges_api_profile', 
                    kwargs={'username': user.username}))
            },
            'awards': {
                'text/html': site_url(user.get_absolute_url()+'#awards'),
                'application/json': site_url(reverse('badges_api_profile_awards', 
                    kwargs={'claimed_by__username': user.username}))
            },
        }


class AnonymousProfileHandler(ProfileHandler, AnonymousBaseHandler):
    pass


class BadgeHandler(BaseHandler):
    anonymous = 'AnonymousBadgeHandler'
    model = Badge
    allowed_methods = ('GET','POST',)
    fields = (
        'links', 'title', 'image', 'description', 
        ('creator', ('username','image', 'links')), 
        'created_at', 'updated_at', 
    )

    def create(self, request):
        """POST to create a new badge"""
        data = request.data

        if 'title' not in data:
            resp = rc.BAD_REQUEST
            resp.write('title required')
            return resp

        new_badge = Badge(
            creator=request.user,
            updated_at=datetime.now(),
            title = data['title'], 
            slug = slugify(data['title']),
            description = data.get('description', ''),
            autoapprove = data.get('autoapprove', False),
            only_creator_can_nominate = 
                data.get('only_creator_can_nominate', False),
        )

        try:
            new_badge.validate_unique()
        except ValidationError, e:
            return rc.DUPLICATE_ENTRY

        try:
            new_badge.full_clean()
            new_badge.save()
            return render_created(self, request, [ new_badge ], 
                site_url(reverse('badges_api_badge', 
                    kwargs={'slug': new_badge.slug})))
        except ValidationError, e:
            resp = rc.BAD_REQUEST
            resp.write('%s' % e)
            return resp

    @classmethod
    def image(handler, badge):
        return { 
            'href': site_url(badge.main_image_url(BADGE_DEFAULT_SIZE)),
            'width': BADGE_DEFAULT_SIZE, 'height': BADGE_DEFAULT_SIZE,
        }

    @classmethod
    def links(handler, badge):
        return {
            'self': {
                'text/html': site_url(badge.get_absolute_url()),
                'application/json': site_url(reverse('badges_api_badge', 
                    kwargs={'slug': badge.slug}))
            },
            'nominations': {
                'text/html': site_url(badge.get_absolute_url()+'#nominations'),
                'application/json': site_url(
                    reverse('badges_api_nomination_collection', 
                    kwargs={'badge__slug': badge.slug}))
            },
            'awards': {
                'text/html': site_url(badge.get_absolute_url()+'#awards'),
                'application/json': site_url(reverse('badges_api_award_collection', 
                    kwargs={'badge__slug': badge.slug}))
            },
        }


class AnonymousBadgeHandler(BadgeHandler, AnonymousBaseHandler):
    allowed_methods = ('GET',)


class NominationHandler(BaseHandler):
    model = BadgeNomination
    fields = (
        'id',
        'links',
        ('badge', ('title', 'links', 'image',)),
        ('nominee', ('username','image',)),
        'nominator',
        'reason_why', 
        'approved',
        ('approved_by', ('username','image',)),
        'approved_why',
        'created_at',
        'updated_at',
    )

    def create(self, request, badge__slug):
        badge = Badge.objects.get(slug = badge__slug)

        data = request.data

        if 'nominee' not in data:
            resp = rc.BAD_REQUEST
            resp.write('nominee required')
            return resp

        if 'username' in data['nominee']:
            nom_user = User.objects.get(username=data['nominee']['username'])
            nominee, created = BadgeAwardee.objects.get_or_create(user=nom_user)
        else:
            resp = rc.BAD_REQUEST
            resp.write('valid nominee required')
            return resp

        new_nomination = badge.nominate(request.user, nominee, 
                data.get('reason_why', ''))

        return render_created(self, request, [ new_nomination ], 
            site_url(reverse('badges_api_nomination', kwargs={
                'badge__slug': badge.slug,
                'id': new_nomination.id,
            })))

    @classmethod
    def resource_uri(handler, obj=None):
        return ('badges_api_nomination', ['slug', 'id'])

    @classmethod
    def links(handler, nomination):
        return {
            'text/html': site_url(nomination.get_absolute_url()),
        }


class BadgeAwardHandler(BaseHandler):
    model = BadgeAward

    @classmethod
    def resource_uri(handler, obj=None):
        return ('badges_api_award', [ 'badge__slug', 'id' ])


class ProfileAwardHandler(BaseHandler):
    model = BadgeAward

    @classmethod
    def resource_uri(handler, obj=None):
        return ('badges_api_profile_awards', [ 'username' ])


