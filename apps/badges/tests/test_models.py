""" """
from django.http import HttpRequest
from django.test import TestCase

from django.contrib.auth.models import User

from pinax.apps.profiles.models import Profile
from pinax.apps.account.models import Account

from badger.apps.badges.models import Badge, BadgeNomination, BadgeAward

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_

class TestBadges(TestCase):

    def setUp(self):
        self.users = {}
        for user_name in ( 'user1', 'user2', 'user3' ):
            self.users[user_name] = User.objects.create(username=user_name)

    def tearDown(self):
        for name, user in self.users.items():
            user.delete()
