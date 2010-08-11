"""Tests for badge feeds"""
import logging
import re
import urlparse
import StringIO
import time

from lxml import etree
from pyquery import PyQuery

from xml.etree import ElementTree
from activitystreams.atom import make_activities_from_feed
from activitystreams.json import make_activities_from_stream_dict
from django.utils import simplejson as json

from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User

from pinax.apps.profiles.models import Profile
from pinax.apps.account.models import Account

from badger.apps.badges.models import Badge, BadgeNomination, BadgeAward

from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from nose.plugins.attrib import attr

from django.contrib.auth.models import User
from pinax.apps.profiles.models import Profile
from pinax.apps.account.models import Account
from badger.apps.badges.models import Badge, BadgeNomination
from badger.apps.badges.models import BadgeAward, BadgeAwardee
from mailer.models import Message, MessageLog
from notification.models import NoticeType, Notice

class TestFeeds(TestCase):

    def setUp(self):
        self.log = logging.getLogger('nose.badger')
        self.browser = Client()

        for user in User.objects.all():
            user.delete()

        self.users = {}
        for name in ( 'user1', 'user2', 'user3'):
            self.users[name] = self.get_user(name)

    def tearDown(self):
        pass

    def test_recent_awards(self):
        """Ensure the recent awards feed parses as an Activity Stream"""
        badge_awards = (
            ( 'badge1', 'user1', 'user2', 'user3' ),
            ( 'badge2', 'user1', 'user3', 'user2' ),
            ( 'badge3', 'user3', 'user1', 'user2' ),
            ( 'badge4', 'user1', 'user1', 'user1' ),
        )
        badges, awards = self.build_awards(badge_awards)
        self.verify_atom_activity_stream(badge_awards,
                '/badges/feeds/atom/recentawards/')
        self.verify_json_activity_stream(badge_awards,
                '/badges/feeds/json/recentawards/')
    
    def test_profile_awards(self):
        """Ensure the award feed for a single profile parses as an Activity Stream"""
        badge_awards = (
            ( 'badge1', 'user1', 'user2', 'user3' ),
            ( 'badge2', 'user2', 'user1', 'user3' ),
            ( 'badge3', 'user1', 'user2', 'user3' ),
            ( 'badge4', 'user2', 'user1', 'user3' ),
        )
        badges, awards = self.build_awards(badge_awards)
        self.verify_atom_activity_stream(badge_awards,
                '/badges/feeds/atom/profiles/user3/awards/')
        self.verify_json_activity_stream(badge_awards,
                '/badges/feeds/json/profiles/user3/awards/')
    
    def test_badge_awards(self):
        """Ensure the award feed for a single badge parses as an Activity Stream"""
        badge_awards = (
            ( 'badge1', 'user1', 'user2', 'user3' ),
            ( 'badge1', 'user2', 'user3', 'user1' ),
            ( 'badge1', 'user3', 'user1', 'user2' ),
        )
        badges, awards = self.build_awards(badge_awards)
        self.verify_atom_activity_stream(badge_awards,
                '/badges/feeds/atom/badges/badge1/awards/')
        self.verify_json_activity_stream(badge_awards,
                '/badges/feeds/json/badges/badge1/awards/')

    #######################################################################

    def get_user(self, username, password=None, email=None):
        """Get a user for the given username, creating it if necessary."""
        if password is None: password = '%s_password' % username
        if email is None: email = '%s@example.com' % username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username, email, password)
        ok_(user is not None, "user should exist")
        return user

    def build_awards(self, badge_awards):
        badges, awards = {}, {}

        for details in badge_awards:
            badge_name, creator_name, nominator_name, nominee_name = details
            
            creator      = self.users[creator_name]
            nominator    = self.users[nominator_name]
            nominee_user = self.users[nominee_name]
            nominee, c   = BadgeAwardee.objects.get_or_create(user=nominee_user)

            try:
                badge = Badge.objects.get(title=badge_name)
            except Badge.DoesNotExist:
                badge = Badge(title=badge_name, creator=creator,
                    description='%s description' % badge_name)
                badge.save()
            badges[badge_name] = badge

            nomination = badge.nominate(nominator, nominee, 
                    '%s nomination reason' % badge_name)
            award = nomination.approve(creator, 
                    '%s approval reason' % badge_name)
            award.claim(nominee_user)

            awards[details] = award

            time.sleep(1)

        return badges, awards

    def verify_activities(self, badge_awards, activities):
        # Ensure feed activity count matches award count
        eq_(len(badge_awards), len(activities))
        
        for details in badge_awards:
            badge_name, creator_name, nominator_name, nominee_name = details
            act = activities.pop()

            # Check the actor for this activity
            eq_(nominee_name, act.actor.name)
            eq_('http://activitystrea.ms/schema/1.0/person', 
                    act.actor.object_type)
            eq_('http://example.com/profiles/profile/%s/' % nominee_name,
                    act.actor.url)

            # Check the verb for this activity
            eq_('http://badger.decafbad.com/activity/1.0/verbs/claim', act.verb)

            # Check the object for this activity
            eq_(badge_name, act.object.name)
            eq_('http://badger.decafbad.com/activity/1.0/objects/badge', 
                    act.object.object_type)
            eq_('http://example.com/badges/badge/%s' % (badge_name),
                    act.object.url)

    def verify_json_activity_stream(self, badge_awards, path):
        resp = self.browser.get(path)
        activities = make_activities_from_stream_dict(json.loads(resp.content))
        self.verify_activities(badge_awards, activities)

    def verify_atom_activity_stream(self, badge_awards, path):
        resp = self.browser.get(path)
        et = ElementTree.parse(StringIO.StringIO(resp.content))
        activities = make_activities_from_feed(et)
        self.verify_activities(badge_awards, activities)

