"""
Feeds for badges
"""
import datetime
import validate_jsonp

#from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.utils.feedgenerator import SyndicationFeed, Atom1Feed, get_tag_uri
import django.utils.simplejson as json
from django.shortcuts import get_object_or_404

from django.utils.translation import ugettext as _

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings

from badges.models import Badge, BadgeNomination
from badges.models import BadgeAward, BadgeAwardee

from avatar.templatetags.avatar_tags import avatar_url
from badges.templatetags.badge_tags import badge_url


class ActivityStreamAtomFeedGenerator(Atom1Feed):
    """Tweaks to Atom feed to include Activity Stream data"""

    def root_attributes(self):
        attrs = super(ActivityStreamAtomFeedGenerator, self).root_attributes()
        attrs['xmlns:activity'] = 'http://activitystrea.ms/spec/1.0/'
        attrs['xmlns:media'] = 'http://purl.org/syndication/atommedia'
        return attrs

    def add_item_elements(self, handler, item):
        """Inject Activity Stream elements into an item"""

        handler.addQuickElement('published', item['pubdate'].isoformat())
        item['pubdate'] = None

        # Author information.
        if item['author_name'] is not None:
            handler.startElement(u"author", {})
            handler.addQuickElement(u"activity:object-type", 
                'http://activitystrea.ms/schema/1.0/person')
            handler.addQuickElement(u"name", item['author_name'])
            if item['author_email'] is not None:
                handler.addQuickElement(u"email", item['author_email'])
            if item['author_link'] is not None:
                handler.addQuickElement(u"uri", item['author_link'])
            handler.addQuickElement(u"id", 
                get_tag_uri(item['author_link'], item['pubdate']))
            handler.addQuickElement(u"link", u"", {
                'type': 'text/html', 'rel':'alternate',
                'href': item['author_link']
            })
            handler.addQuickElement(u"link", u"", {
                'type': 'image/jpeg', 'rel':'photo',
                'media:width': '64', 'media:height': '64',
                'href': 'http://%s%s' % (
                    Site.objects.get_current().domain, 
                    avatar_url(item['obj'].claimed_by, 64)
                ),
            })
            avatar_href = avatar_url(item['obj'].claimed_by, 64)
            if avatar_href.startswith('/'):
                avatar_href = 'http://%s%s' % (
                    Site.objects.get_current().domain, avatar_href
                )
            handler.addQuickElement(u"link", u"", {
                'type': 'image/jpeg', 'rel':'preview',
                'media:width': '64', 'media:height': '64',
                'href': avatar_href,
            })
            handler.endElement(u"author")
        item['author_name'] = None

        handler.addQuickElement('activity:verb', item['activity']['verb'])

        a_object = item['activity']['object']
        handler.startElement(u"activity:object", {})
        handler.addQuickElement(u"activity:object-type", a_object['object-type'])
        handler.addQuickElement(u"title", a_object['name'])
        handler.addQuickElement(u"id", get_tag_uri(a_object['link'], 
                item['pubdate']))
        handler.addQuickElement(u"link", '', {
            'href': a_object['link'], 'rel':'alternate', 'type':'text/html'
        })
        handler.addQuickElement(u"link", u"", {
            'type': 'image/jpeg', 'rel':'preview',
            'media:width':  a_object['preview']['width'],
            'media:height': a_object['preview']['height'],
            'href': a_object['preview']['href'],
        })
        handler.endElement(u"activity:object")

        super(ActivityStreamAtomFeedGenerator, self).add_item_elements(handler, item)


class ActivityStreamJSONFeedGenerator(SyndicationFeed):
    mime_type = 'application/json'

    def _encode_complex(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

    def write(self, outfile, encoding):
        # Check for a callback param, validate it before use
        callback = self.feed['request'].GET.get('callback', None)
        if callback is not None:
            if not validate_jsonp.is_valid_jsonp_callback_value(callback):
                callback = None

        items_out = []
        for item in self.items:
            
            avatar_href = avatar_url(item['obj'].claimed_by, 64)
            if avatar_href.startswith('/'):
                avatar_href = 'http://%s%s' % (
                    Site.objects.get_current().domain, avatar_href
                )

            a_object = item['activity']['object']

            item_out = {
                'postedTime': item['pubdate'],
                'verb': item['activity']['verb'],
                'actor': {
                    'objectType': 'http://activitystrea.ms/schema/1.0/person',
                    'id': get_tag_uri(item['author_link'], item['pubdate']),
                    'displayName': item['author_name'],
                    'permalinkUrl': item['author_link'],
                    'image': {
                        'url': avatar_href, 
                        'width':'64', 
                        'height':'64',
                    }
                },
                'object': {
                    'objectType': a_object['object-type'],
                    'id': get_tag_uri(a_object['link'], item['pubdate']),
                    'displayName': a_object['name'],
                    'permalinkUrl': a_object['link'],
                    'image': {
                        'url': a_object['preview']['href'],
                        'width': a_object['preview']['width'],
                        'height': a_object['preview']['height'],
                    }
                },
            }
            items_out.append(item_out)

        data = {
            "items": items_out
        }

        if callback: outfile.write('%s(' % callback)
        outfile.write(json.dumps(data, default=self._encode_complex))
        if callback: outfile.write(')')


class AwardActivityStreamFeed(Feed):
    """Tweaks to standard feed to include Activity Stream info 
    for lists of badge awards"""
    feed_type = ActivityStreamAtomFeedGenerator

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super(AwardActivityStreamFeed, self).__call__(request, *args, **kwargs)

    def feed_extra_kwargs(self, obj):
        return { 'request': self.request }

    def item_author_name(self, item):
        return '%s' % item.claimed_by

    def item_author_link(self, item):
        current_site = Site.objects.get(id=settings.SITE_ID)
        return 'http://%s%s' % (Site.objects.get_current().domain, 
                item.claimed_by.get_absolute_url())

    def item_pubdate(self, item):
        return item.updated_at
        
    def item_title(self, item):
        return '%s claimed the badge "%s"' % (item.claimed_by, item.badge)

    def item_description(self, item):
        # TODO: Stick this in a template?
        avatar_img = avatar_url(item.claimed_by, 64)
        if avatar_img.startswith('/'):
            avatar_img = 'http://%s%s' % (
                Site.objects.get_current().domain, avatar_img)
        badge_img = badge_url(item.badge, 64) 
        if badge_img.startswith('/'):
            badge_img = 'http://%s%s' % (
                Site.objects.get_current().domain, badge_img) 
        return """
            <a href="%(claimed_by_url)s"><img src="%(avatar_img)s" width="64" height="64" /> %(claimed_by)s</a>
            <a href="%(award_url)s">claimed</a> the badge
            <a href="%(badge_url)s">"%(badge_title)s" <img src="%(badge_img)s" width="64" height="64" /></a>
        """ % {
            'avatar_img': avatar_img,
            'badge_img': badge_img,
            'claimed_by': item.claimed_by,
            'claimed_by_url': item.claimed_by.get_absolute_url(),
            'badge_title': item.badge.title,
            'badge_url': item.badge.get_absolute_url(),
            'award_url': item.get_absolute_url(),
        }

    def item_extra_kwargs(self, obj):
        return { 
            'obj': obj,
            'activity': {
                'verb': 'http://badger.decafbad.com/activity/1.0/verbs/claim',
                'object': { 
                    'object-type': 
                        'http://badger.decafbad.com/activity/1.0/objects/badge',
                    'name': obj.badge.title,
                    'link': 'http://%s%s' % (
                        Site.objects.get_current().domain, 
                        obj.badge.get_absolute_url()
                    ),
                    'preview': {
                        'width': '64', 'height': '64',
                        'href': 'http://%s%s' % (
                            Site.objects.get_current().domain, 
                            badge_url(obj.badge, 64) 
                        ),
                    },
                },
            },
        }


class RecentlyClaimedAwardsFeed(AwardActivityStreamFeed):
    """Feed of recently claimed badge awards"""

    title     = _('Recently claimed badges')
    subtitle  = _('Badges recently claimed by people')
    link      = '/'

    def items(self):
        return BadgeAward.objects.filter(claimed=True).exclude(hidden=True)\
                .order_by('-updated_at')[:15]


class AwardsClaimedForProfileFeed(AwardActivityStreamFeed):

    title = _('Recently claimed badges')
    link = '/'

    def get_object(self, request, username):
        user = get_object_or_404(User, username=username)
        self.title = "%s's recently claimed badges" % user.username
        return user

    def items(self, user):
        return BadgeAward.objects.filter(claimed_by=user, claimed=True)\
                .exclude(hidden=True).order_by('-updated_at')[:15]


class AwardsClaimedForBadgeFeed(AwardActivityStreamFeed):

    title = _('Recent claims for badge')
    link = '/'

    def get_object(self, request, slug):
        badge = get_object_or_404(Badge, slug=slug)
        self.title = 'Recent claims for the badge "%s"' % badge.title
        return badge

    def items(self, badge):
        return BadgeAward.objects.filter(badge=badge, claimed=True)\
                .exclude(hidden=True).order_by('-updated_at')[:15]


class RecentlyClaimedAwardsJSONFeed(RecentlyClaimedAwardsFeed):
    feed_type = ActivityStreamJSONFeedGenerator


class AwardsClaimedForProfileJSONFeed(AwardsClaimedForProfileFeed):
    feed_type = ActivityStreamJSONFeedGenerator


class AwardsClaimedForBadgeJSONFeed(AwardsClaimedForBadgeFeed):
    feed_type = ActivityStreamJSONFeedGenerator

