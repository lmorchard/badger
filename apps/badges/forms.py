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
from uni_form.helpers import FormHelper, Submit, Reset

class MyModelForm(forms.ModelForm):
    def as_ul(self):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output(
            normal_row = u'<li%(html_class_attr)s>%(label)s %(field)s<p class="help">%(help_text)s</p>%(errors)s</li>',
            error_row = u'<li>%s</li>',
            row_ender = '</li>',
            help_text_html = u' %s',
            errors_on_separate_row = False)


class MyForm(forms.Form):
    def as_ul(self):
        "Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."
        return self._html_output(
            normal_row = u'<li%(html_class_attr)s>%(label)s %(field)s<p class="help">%(help_text)s</p>%(errors)s</li>',
            error_row = u'<li>%s</li>',
            row_ender = '</li>',
            help_text_html = u' %s',
            errors_on_separate_row = False)


class BadgeForm(MyModelForm):

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


class BadgeNominationForm(MyForm):
    nominee = UsernameOrEmailField(max_length=100, required=True,
        help_text=_('member user name or any email address'))
    reason_why = forms.CharField(required=True,
        widget=forms.widgets.Textarea(),
        help_text=_('describe how this person has come to deserve this award'))

    def clean(self):
        """Ensure that duplicate nominations are not accepted"""
        cleaned_data = super(BadgeNominationForm, self).clean()
        
        try:
            if 'nominee' in self.cleaned_data:
                nominee = BadgeAwardee.objects.get_by_user_or_email(
                        self.cleaned_data['nominee'])
                existing_nomination = BadgeNomination.objects.get(
                    badge=self.context['badge'], 
                    nominee=nominee
                )
                raise ValidationError(
                    _('This person has already been nominated for this badge.'))

        except ObjectDoesNotExist:
            pass

        return cleaned_data


class BadgeNominationDecisionForm(MyForm):
    reason_why = forms.CharField(required=True,
        #widget=forms.widgets.Textarea(),
        help_text=_('briefly explain your decision'))

