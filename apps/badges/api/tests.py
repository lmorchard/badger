"""Tests for badge API"""
import logging
import re
import urlparse
import urllib
import StringIO
import time
import random
from oauth import oauth

from oauth.oauth import ( OAuthToken, OAuthConsumer, OAuthRequest,
        OAuthSignatureMethod_HMAC_SHA1, OAuthSignatureMethod_PLAINTEXT )

from lxml import etree
from pyquery import PyQuery

from django.utils import simplejson as json

from django.http import HttpRequest
from django.test import TestCase
from django.test.client import FakePayload, Client
from django.template.defaultfilters import slugify

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from pinax.apps.profiles.models import Profile
from pinax.apps.account.models import Account

from badges.models import ( Badge, BadgeNomination, BadgeAward, 
        BadgeAwardee, badge_file_path )

# HACK: This is probably a mistake, but the site_url utility func seems just as
# useful in tests.
from badges.api.handlers import site_url

from piston.models import Consumer, Token 


class TestAPI(TestCase):

    API_BASE_PATH = '/badges/api'

    def setUp(self):
        self.log = logging.getLogger('nose.badger')
        self.browser = Client()

        for x in User.objects.all(): x.delete()
        for x in Badge.objects.all(): x.delete()
        for x in Consumer.objects.all(): x.delete()

        self.site = Site.objects.get_current()
        self.site.domain = 'testserver'
        self.site.save()

        self.users = {}
        for name in ( 'user1', 'user2', 'user3'):
            self.users[name] = self.get_user(name)

        badge_awards = (
            ( 'badge1', 'user1', 'user2', 'user3', True ),
            ( 'badge2', 'user2', 'user1', 'user3', False ),
            ( 'badge3', 'user1', 'user2', 'user3', True ),
            ( 'badge4', 'user2', 'user1', 'user3', False ),
        )
        self.badges, self.awards = self.build_awards(badge_awards)

        self.consumer_key    = 'keykeykey'
        self.consumer_secret = 'secretsecretsecret'

        self.authorize_oauth_app()

    def tearDown(self):
        pass

    def test_index(self):
        """Exercise the index API resource"""
        path = '/badges/api/'
        c = Client()

        for use_oauth in ( True, False ):
            data = self.api_GET('/', {}, use_oauth)[0]

            # This stuff should appear regardless of auth.
            ok_('profiles' in data)
            eq_(site_url('/badges/api/profiles/'), data['profiles'])
            ok_('badges' in data)
            eq_(site_url('/badges/api/badges/'), data['badges'])
            ok_('docs' in data)
            eq_(site_url('/badges/api/docs/'), data['docs'])

            if use_oauth:
                # If auth accepted, there should be links to the auth user.
                ok_('authenticated' in data)
                ok_('application/json' in data['authenticated'])
                eq_(site_url('/badges/api/profiles/user1/'), 
                        data['authenticated']['application/json'])

    def test_get_profiles(self):
        """Exercise the profile and profile collection API resources"""
        users = sorted(self.users.values(), key=lambda x: x.username)
        for use_oauth in ( True, False ):
            # Both auth and non-auth cases should be the same.
            collections = [
                self.api_GET('/profiles/', {}, use_oauth)[0],
                [ self.api_GET('/profiles/%s/' % u.username, {}, use_oauth)[0][0] 
                    for u in users ]
            ]
            for items in collections:
                eq_(len(users), len(items))
                items.sort(key=lambda b: b['username'])
                for idx in range(0, len(items)):
                    e_user, r_user = users[idx], items[idx]
                    # TODO: Compare more attributes?
                    eq_(e_user.username, r_user['username'])
                    eq_(site_url(e_user.get_absolute_url()), 
                        r_user['links']['self']['text/html'])
                    eq_(site_url('/badges/api/profiles/%s/' % e_user.username), 
                        r_user['links']['self']['application/json'])


    def test_get_badges(self):
        """Exercise the badge and badge collection API resources"""
        badges = sorted(self.badges.values(), key=lambda b: b.title)
        for use_oauth in ( True, False ):
            # Both auth and non-auth cases should be the same.
            collections = [
                self.api_GET('/badges/', {}, use_oauth)[0],
                [ self.api_GET('/badges/%s/' % b.title, {}, use_oauth)[0][0]
                    for b in badges ]
            ]
            for items in collections:
                eq_(len(badges), len(items))
                items.sort(key=lambda b: b['title'])
                for idx in range(0, len(items)):
                    e_badge, r_badge = badges[idx], items[idx]
                    # TODO: Compare more attributes?
                    eq_(e_badge.title, r_badge['title'])
                    eq_(site_url(e_badge.get_absolute_url()), 
                        r_badge['links']['self']['text/html'])
                    eq_(site_url('/badges/api/badges/%s/' % e_badge.slug), 
                        r_badge['links']['self']['application/json'])

    def test_create_badge(self):
        """Exercise creating a badge via the API"""
        props = {
            'title': 'New Sample Badge',
            'description': 'This is a badge created via API',
        }
        data, resp = self.api_POST('/badges/', body=props, use_oauth=True)

        eq_(props['title'], data[0]['title'])
        eq_(props['description'], data[0]['description'])
        eq_(site_url('/badges/api/badges/%s/' % slugify(props['title'])), 
            resp['location'])

        badge = Badge.objects.get(title=props['title'])
        eq_(props['title'], badge.title)
        eq_(props['description'], badge.description)

        # TODO: implement and test image upload

    @attr('current')
    def test_create_nomination(self):
        """Exercise nominating a user for a badge"""
        badge = self.badges['badge4']
        badge_url_path = '/badges/%s/' % badge.slug

        data, resp = self.api_GET(badge_url_path)
        ok_(data[0]['links']['nominations']['application/json'],
            site_url('/badges/api/badges/%s/nominations/' % badge.slug))

        nom_data = { 
            'nominee': { 'username': 'user2' },
            'reason_why': 'Extreme awesomeness'
        }
        data, resp = self.api_POST('/badges/%s/nominations/' % badge.slug, 
            use_oauth=True, body = nom_data)

        self.log.debug('%s' % resp)

        nomination = BadgeNomination.objects.get(
                nominee__user__username='user2', badge=badge)
        eq_(nom_data['reason_why'], nomination.reason_why)

        # TODO: nominate by email address


    #######################################################################

    def api_GET(self, path, params=None, use_oauth=False, parse_json=True):
        c = Client()
        params = params or {}
        full_path = self.API_BASE_PATH + path
        if use_oauth:
            params.update(self.oauth_params(full_path, params))
        response = c.get(full_path, params)

        if parse_json:
            try:
                return ( json.loads(response.content), response )
            except ValueError, e:
                return ( None, response )
        else:
            return ( response.content, response )

    def api_POST(self, path, params=None, body='', use_oauth=False, 
            extra=None, follow=True, parse_json=True):
        c = Client()
        params = params or {}
        extra = extra or {}
        body = body or ''

        if type(body) != str:
            body = json.dumps(body)

        full_path = self.API_BASE_PATH + path
        content_type = extra.get('CONTENT_TYPE', 'application/json')

        r = {
            'CONTENT_LENGTH': len(body),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      urllib.unquote(full_path),
            'QUERY_STRING':   urllib.urlencode(params),
            'REQUEST_METHOD': 'POST',
            'wsgi.input':     FakePayload(body),
        }
        r.update(extra)

        if use_oauth:
            o_params = self.oauth_params(full_path, params_in=params, 
                    body=body, http_method='POST')
            r['HTTP_AUTHORIZATION'] = 'OAuth realm="API", %s' % (', '.join(
                '%s="%s"' % i for i in o_params.items() if i[0].startswith('oauth')
            ))

        response = c.request(**r)
        if follow:
            response = c._handle_redirects(response)

        if parse_json:
            try:
                return ( json.loads(response.content), response )
            except ValueError, e:
                return ( None, response )
        else:
            return ( response.content, response )

    def oauth_params(self, path, params_in=None, body='', http_method='GET'):
        """Build parameters to use in authenticating via OAuth with test client"""
        url = 'http://testserver%s' % (path)

        params = {
            'oauth_consumer_key': self.consumer.key,
            'oauth_token': self.access_token.key,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_version': '1.0',
        }
        if params_in is not None:
            params.update(params_in)

        parts = urlparse.urlparse(url)
        if parts.query:
            params.update(urlparse.parse_qs(parts.query))

        oauth_request = OAuthRequest.from_token_and_callback(
            self.access_token, parameters=params,
            http_method=http_method,
            http_url=urlparse.urlunparse((
                parts.scheme, parts.netloc, parts.path,
                '', '', parts.fragment,
            )), 
        )
        signature_method = OAuthSignatureMethod_HMAC_SHA1()
        #signature_method = OAuthSignatureMethod_PLAINTEXT()
        signature = signature_method.build_signature(
            oauth_request, self.consumer, self.access_token
        )
        params['oauth_signature'] = signature

        new_url = urlparse.urlunparse((
            parts.scheme, parts.netloc, parts.path,
            '', urllib.urlencode(params), parts.fragment,
        ))
        return params

    def get_user(self, username, password=None, email=None):
        """Get a user for the given username, creating it if necessary."""
        if password is None: password = '%s_password' % username
        if email is None: email = '%s@testserver' % username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username, email, password)
        ok_(user is not None, "user should exist")
        return user

    def build_awards(self, badge_awards):
        badges, awards = {}, {}

        for details in badge_awards:
            badge_name, creator_name, nominator_name, nominee_name, claimed = details
            
            creator      = self.users[creator_name]
            nominator    = self.users[nominator_name]
            nominee_user = self.users[nominee_name]
            nominee, c   = BadgeAwardee.objects.get_or_create(user=nominee_user)

            try:
                badge = Badge.objects.get(title=badge_name)
            except Badge.DoesNotExist:
                badge = Badge(title=badge_name, creator=creator,
                    slug=slugify(badge_name),
                    description='%s description' % badge_name)
                badge.save()
            badges[badge_name] = badge

            nomination = badge.nominate(nominator, nominee, 
                    '%s nomination reason' % badge_name)
            award = nomination.approve(creator, 
                    '%s approval reason' % badge_name)
            if claimed:
                award.claim(nominee_user)

            awards[details] = award

            time.sleep(1)

        return badges, awards

    def authorize_oauth_app(self):
        
        user = self.users['user1']

        # Create a new consumer
        # TODO: Make a test that does this through the (future) control panel
        consumer = Consumer(name="test_app", description="Test App",
            key=self.consumer_key, secret=self.consumer_secret, user=user)
        consumer.save()

        # Get a request token.
        params = {
            'oauth_consumer_key': self.consumer_key,
            'oauth_signature_method': 'PLAINTEXT',
            'oauth_signature': '%s&' % self.consumer_secret,
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': 'requestnonce',
            'oauth_version': '1.0',
            'scope': 'photos', # custom argument to specify Protected Resource
        }
        resp = self.browser.get("/badges/api/oauth/request_token/", params)
        data = urlparse.parse_qs(resp.content)
        token_key = data['oauth_token'][0]
        token_secret = data['oauth_token_secret'][0]
        
        # Get the form to approve access for the token.
        self.browser.login(username='user1', password='user1_password')
        params = {
            'oauth_token': token_key,
            'oauth_callback': 'http://testserver/callback',
            'authorize_access': '1'
        }
        resp = self.browser.get("/badges/api/oauth/authorize/", params)

        # Dig out the form params and approve access for the token.
        # This helps account for the inevitable CSRF crumb present.
        page = PyQuery(resp.content)
        form = page('form[action="/badges/api/oauth/authorize/"]')
        params = dict( (i.name, i.value) for i in form('input') )
        params['authorize_access'] = 1
        resp = self.browser.post("/badges/api/oauth/authorize/", params)

        # Parse out the verifier from the redirect
        url_parts = urlparse.urlparse(resp['location'])
        data = urlparse.parse_qs(url_parts.query)
        eq_(token_key, data['oauth_token'][0])
        token_verifier = data['oauth_verifier'][0]

        # Make sure the token's been approved.
        t = Token.objects.get(key=token_key)
        ok_(t.is_approved)

        # Make a request to trade token for access token.
        params = {
            'oauth_consumer_key': self.consumer_key,
            'oauth_token': token_key,
            'oauth_signature_method': 'PLAINTEXT',
            'oauth_signature': '%s&%s' % (self.consumer_secret, token_secret),
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': 'accessnonce',
            'oauth_version': '1.0',
            'oauth_verifier': token_verifier,
        }
        resp = self.browser.get("/badges/api/oauth/access_token/", params)
        data = urlparse.parse_qs(resp.content)

        access_token_key = data['oauth_token'][0]
        access_token_secret = data['oauth_token_secret'][0]

        # Build a request for a service
        self.access_token = OAuthToken(access_token_key, access_token_secret)
        self.consumer = OAuthConsumer(self.consumer_key, self.consumer_secret)

