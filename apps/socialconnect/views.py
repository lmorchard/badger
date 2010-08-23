import urllib, urllib2
import cgi
import os

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, authenticate
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site

from django.utils import simplejson as json
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib import messages

from oauthtwitter import OAuthApi
from oauth import oauth
import oauthtwitter

from pinax.apps.account.utils import get_default_redirect, user_display
from pinax.apps.account.views import login as account_login

from socialconnect.utils import Router, ViewObject
from socialconnect.forms import OauthSignupForm
from socialconnect.models import UserOauthAssociation

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', 'YOUR_KEY')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', 'YOUR_SECRET')

FACEBOOK_CONSUMER_KEY = getattr(settings, 'FACEBOOK_CONSUMER_KEY', 'YOUR_KEY')
FACEBOOK_CONSUMER_SECRET = getattr(settings, 'FACEBOOK_CONSUMER_SECRET', 'YOUR_SECRET')


redirect_field_name = "next"

class SocialConnectView(ViewObject):

    def do_signin(self, request):
        """Perform sign in via OAuth"""
        return HttpResponseRedirect(self.get_signin_url(request))

    def do_callback(self, request):
        """Handle response from OAuth permit/deny"""
        # TODO: Handle OAuth denial!
        profile = self.get_profile_from_callback(request)
        if not profile: return HttpResponse(status=400)

        request.session[self.session_profile] = profile

        success_url = get_default_redirect(request, redirect_field_name)

        try:
            # Try looking for an association to perform a login.
            assoc = UserOauthAssociation.objects.filter(
                auth_type=self.auth_type,
                profile_id=profile['id'], 
                username=profile['username']
            ).get()
            self.log_in_user(request, assoc.user)
            return HttpResponseRedirect(success_url)

        except UserOauthAssociation.DoesNotExist:
            # No association found, so...
            if not request.user.is_authenticated():
                # If no login session, bounce to registration
                return HttpResponseRedirect(reverse(
                    self.urlname_pattern % 'register'
                ))
            else:
                # If there's a login session, create an association to the
                # currently logged in user.
                assoc = self.create_association(request, request.user, profile)
                del request.session[self.session_profile]
                return HttpResponseRedirect(success_url)

    def get_registration_form_class(self, request):
        return OauthSignupForm

    def do_register(self, request):
        """Handle registration with association"""
        # Ensure that Twitter signin details are present in the session     
        profile = request.session.get(self.session_profile, None)
        if not profile: return HttpResponse(status=400)

        RegistrationForm = self.get_registration_form_class(request)
        success_url = get_default_redirect(request, redirect_field_name)

        if request.method != "POST":
            # Pre-fill form with suggested info based in Twitter signin
            form = RegistrationForm(initial = self.initial_from_profile(profile))

        else:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(request=request)
                assoc = self.create_association(request, user, profile)
                self.log_in_user(request, user)
                return HttpResponseRedirect(success_url)

        return render_to_response('socialconnect/register.html', {
            'form': form,
            'auth_label': self.auth_label,
            'signin_url': reverse(self.urlname_pattern % 'signin'),
            "action": request.path,
        }, context_instance=RequestContext(request))

    def create_association(self, request, user, profile):
        """Create an association between this user and the given profile"""
        assoc = UserOauthAssociation(
            user=user,
            auth_type=self.auth_type,
            profile_id=profile['id'], 
            username=profile['username'],
            access_token=profile['access_token']
        )
        assoc.save()
        messages.add_message(request, messages.SUCCESS,
            ugettext("""
                Successfully associated %(user)s with %(auth_label)s 
                screen name %(username)s.
            """) % {
                "user": user_display(request.user),
                "auth_label": self.auth_label,
                "username": profile['username']
            }
        )

    def suggest_nickname(self, nickname):
        "Return a suggested nickname that has not yet been taken"
        from django.contrib.auth.models import User
        if not nickname:
            return ''
        original_nickname = nickname
        suffix = None
        while User.objects.filter(username = nickname).count():
            if suffix is None:
                suffix = 1
            else:
                suffix += 1
            nickname = original_nickname + str(suffix)
        return nickname

    def log_in_user(self, request, user):
        # Remember, openid might be None (after registration with none set)
        from django.contrib.auth import login
        # Nasty but necessary - annotate user and pretend it was the regular 
        # auth backend. This is needed so django.contrib.auth.get_user works:
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

class TwitterAuthView(SocialConnectView):
    auth_type = "twitter"
    auth_label = _("Twitter")

    urlname_pattern = 'auth_twitter_%s'
    
    consumer_key = TWITTER_CONSUMER_KEY
    consumer_secret = TWITTER_CONSUMER_SECRET

    session_access_token = 'twitter_access_token'
    session_profile = 'twitter_profile'

    def get_signin_url(self, request):
        twitter = OAuthApi(self.consumer_key, self.consumer_secret)
        request_token = twitter.getRequestToken()
        request.session['twitter_request_token'] = request_token.to_string()
        return twitter.getSigninURL(request_token)

    def get_profile_from_callback(self, request):
        """Extract the access token and profile details from OAuth callback"""
        request_token = request.session.get('twitter_request_token', None)
        if not request_token: return None

        token = oauth.OAuthToken.from_string(request_token)
        if token.key != request.GET.get('oauth_token', 'no-token'):
            return HttpResponse(status=400)

        twitter = OAuthApi(self.consumer_key, self.consumer_secret, token)
        access_token = twitter.getAccessToken()

        twitter = oauthtwitter.OAuthApi(self.consumer_key, 
                self.consumer_secret, access_token)
        try:
            profile = twitter.GetUserInfo()
        except:
            return None

        return {
            'access_token': access_token.to_string(),
            'id': profile.id,
            'username': profile.screen_name,
            'fullname': profile.name,
            'email': '',
        }

    def initial_from_profile(self, profile):
        fullname = profile['fullname']
        first_name, last_name = '', ''
        if fullname:
            bits = fullname.split()
            first_name = bits[0]
            if len(bits) > 1:
                last_name = ' '.join(bits[1:])
        return {
            'username': self.suggest_nickname(profile.get('username','')),
            'first_name': first_name,
            'last_name': last_name,
            'email': ''
        }


class FacebookAuthView(SocialConnectView):
    auth_type = "facebook"
    auth_label = _("Facebook")

    urlname_pattern = 'auth_facebook_%s'

    consumer_key = FACEBOOK_CONSUMER_KEY
    consumer_secret = FACEBOOK_CONSUMER_SECRET

    session_access_token = 'facebook_access_token'
    session_profile = 'facebook_profile'

    def get_signin_url(self, request):
        args = {
            'client_id': self.consumer_key,
            'redirect_uri': 'http://%s%s' % (
                Site.objects.get_current().domain, 
                reverse('auth_facebook_callback'),
            )
        }
        return ("https://graph.facebook.com/oauth/authorize?" + 
            urllib.urlencode(args))

    def get_profile_from_callback(self, request):

        code = request.GET.get('code', None)
        args = {
            'client_id': self.consumer_key,
            'client_secret': self.consumer_secret,
            'redirect_uri': 'http://%s%s' % (
                Site.objects.get_current().domain, 
                reverse('auth_facebook_callback'),
            ),
            'code': code,
        }
        access_token_url = ()
        response = cgi.parse_qs(urllib2.urlopen(
            "https://graph.facebook.com/oauth/access_token?" + 
            urllib.urlencode(args)
        ).read())

        access_token = response["access_token"][-1]
        profile = json.load(urllib2.urlopen("https://graph.facebook.com/me?" +
            urllib.urlencode(dict(access_token=access_token))))

        return {
            'access_token': access_token,
            'id': profile['id'],
            'username': os.path.basename(profile.get('link','')),
            'fullname': profile.get('name', ''),
            'first_name': profile.get('first_name', ''),
            'last_name': profile.get('last_name', ''),
            'email': '',
        }

    def initial_from_profile(self, profile):
        return {
            'username': self.suggest_nickname(profile.get('username','')),
            'first_name': profile.get('first_name', ''),
            'last_name': profile.get('last_name', ''),
            'email': ''
        }
