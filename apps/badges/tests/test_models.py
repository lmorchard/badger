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

    def test_create_badge(self):
        """Exercise simple creation of badges"""
        p1 = Profile.objects.get(user=self.users['user1'])
        a1 = Account.objects.get(user=self.users['user1'])

        b1 = Badge.objects.create(
            creator = self.users['user1'],
            title = "First test passed!",
            description = "Congratulations, the first test passed"
        )

        b2 = Badge.objects.create(
            creator = self.users['user2'],
            title = "Second test passed!",
            description = "Congratulations, the second test passed"
        )

        b3 = Badge.objects.create(
            creator = self.users['user3'],
            title = "Third test passed!",
            description = "Congratulations, the third test passed"
        )

    def test_badge_nomination(self):
        ok_(False, "TODO")

    def test_badge_award(self):
        ok_(False, "TODO")

    def test_tags_on_badges(self):
        ok_(False, "TODO")

    def test_comments_on_badges(self):
        ok_(False, "TODO")

