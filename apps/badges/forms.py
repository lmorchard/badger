""" """
from django import forms

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from badger.apps.badges.models import Badge, BadgeNomination
from django.core import validators
from django.core.exceptions import ValidationError


class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = ('title', 'description', 'tags')

def username_or_email_validator(value):
    pass

class UsernameOrEmailField(forms.CharField):

    def validate(self, value):
        super(UsernameOrEmailField, self).validate(value)
        try:
            validators.validate_email(value)
        except ValidationError:
            try:
                user = User.objects.filter(username__exact=value).get()
            except User.DoesNotExist:
                raise ValidationError(_('Enter a valid email address or user name'))

    def clean(self, value):
        value = super(UsernameOrEmailField, self).clean(value)
        try:
            validators.validate_email(value)
            return value
        except ValidationError:
            try:
                user = User.objects.filter(username__exact=value).get()
                return user
            except User.DoesNotExist:
                return None

class BadgeNominationForm(forms.Form):
    nominee = UsernameOrEmailField(
        max_length=100, required=True,
        help_text=_('any email address or registered user name')
    )
    reason_why = forms.CharField(widget=forms.widgets.Textarea(), required=True)
