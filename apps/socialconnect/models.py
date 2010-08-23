from django.db import models

class UserOauthAssociation(models.Model):
    user = models.ForeignKey('auth.User')
    auth_type = models.CharField(max_length = 32, null=True)
    profile_id = models.CharField(max_length = 255, null=True)
    username = models.CharField(max_length = 255, null=True)
    access_token = models.CharField(max_length = 255, null=True)
    created = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return u'%s can log in with %s %s (%s)' % (
            self.user, self.auth_type, self.username, self.profile_id 
        )
