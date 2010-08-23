import re

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, ugettext

from pinax.apps.account.forms import SignupForm

class OauthSignupForm(SignupForm):
    
    def __init__(self, *args, **kwargs):
        # remember provided (validated!) OpenID to attach it to the new user
        # later.
        self.openid = kwargs.pop("openid", None)
        # pop these off since they are passed to this method but we can't
        # pass them to forms.Form.__init__
        kwargs.pop("reserved_usernames", [])
        kwargs.pop("no_duplicate_emails", False)
        
        super(OauthSignupForm, self).__init__(*args, **kwargs)
        
        # these fields make no sense in OpenID
        del self.fields["password1"]
        del self.fields["password2"]

