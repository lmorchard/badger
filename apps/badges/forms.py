from django import forms

from django.contrib.auth.models import User
from badger.apps.badges.models import Badge, BadgeNomination

class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = ( 'title', 'description', 'tags' )

class UserField(forms.CharField):

    def clean(self, value):
        
        if not value:
            return None
        if isinstance(value, (User)):
            return value
        try:
            return User.objects.get(username__exact=value)
        except User.DoesNotExist:
            return None

class BadgeNominationForm(forms.ModelForm):
    nominee = UserField()

    class Meta:
        model = BadgeNomination
        fields = ('nominee', 'reason_why')

        
