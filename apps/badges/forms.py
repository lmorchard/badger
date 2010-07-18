""" """
from django import forms

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from badger.apps.badges.models import Badge, BadgeNomination
from badger.apps.badges.models import BadgeAwardee, BadgeAward
from django.core import validators
from django.core.exceptions import ValidationError


class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = ('title', 'description', 'autoapprove', 'tags')

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
                raise ValidationError(
                        _('Enter a valid email address or user name'))

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

    def clean(self):
        """Ensure that duplicate nominations are not accepted"""
        cleaned_data = super(BadgeNominationForm, self).clean()
        
        try:
            nominee = BadgeAwardee.objects.get_by_user_or_email(
                    self.cleaned_data['nominee'])
            existing_nomination = BadgeNomination.objects.get(
                badge=self.context['badge'], 
                nominator=self.context['nominator'],
                nominee=nominee
            )
            raise ValidationError(
                _('This person has already been nominated for this badge.'))

        except ObjectDoesNotExist:
            pass

        return cleaned_data
