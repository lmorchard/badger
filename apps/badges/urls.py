from django.conf.urls.defaults import *

from django.views.generic.list_detail import object_list

from tagging.views import tagged_object_list

from badges.models import Badge

from badges.feeds import RecentlyClaimedAwardsFeed, RecentlyClaimedAwardsJSONFeed
from badges.feeds import AwardsClaimedForProfileFeed, AwardsClaimedForProfileJSONFeed
from badges.feeds import AwardsClaimedForBadgeFeed, AwardsClaimedForBadgeJSONFeed

from voting.views import vote_on_object

urlpatterns = patterns("badges.views",

    url(r'^$', 'index', name='badge_index'),

    url(r'^all/$', object_list, 
        dict(queryset=Badge.objects.all(), template_object_name='badge', 
            template_name='badges/badge_list.html', paginate_by=25, 
            allow_empty=True), 
        name='badge_browse'),

    url(r'^tag/(?P<tag>[^/]+)/$', tagged_object_list,
        dict(queryset_or_model=Badge, paginate_by=25, allow_empty=True,
             template_object_name='badge'),
        name='badge_tag'),

    url(r'^badge/(?P<slug>[^/]+)/(?P<direction>up|down|clear)vote/?$', vote_on_object,
        dict(slug_field='slug', model=Badge, template_object_name='badge', 
            allow_xmlhttprequest=True),
        name='badge_vote'),

    url(r"^create$", "create", 
        name="create_badge"),
    url(r"^verify/(.*)$", "awardee_verify", 
        name="awardee_verify"),

    url(r"^badge/(.*)/nominations/$", "nomination_create", 
        name="badge_nomination_create"),
    url(r"^badge/(.*)/nominations/(.*)$", "nomination_details", 
        name="badge_nomination"),
    #url(r"^badge/(.*)/awards/$", "award_list", 
    #    name="badge_award_recent"),
    url(r"^badge/(.*)/awards/(.*)/$", "award_history", 
        name="badge_award_list"),
    url(r"^badge/(.*)/awards/(.*)/showhide$", "award_show_hide_bulk", 
        name="badge_award_show_hide"),
    url(r"^badge/(.*)/awards/(.*)/(.*)$", "award_details", 
        name="badge_award"),
    url(r"^badge/(.*)/awards/(.*)/(.*)/showhide$", "award_show_hide_single", 
        name="badge_award_show_hide_single"),
    url(r"^badge/(.*)/edit$", "edit", 
        name="badge_edit"),
    url(r"^badge/(.*)$", "badge_details", 
        name="badge_details"),

    (r'^api/', include('badges.api.urls')),

    url(r'feeds/atom/recentawards/', RecentlyClaimedAwardsFeed(), 
        name="badge_feed_recentawards"),
    url(r'feeds/atom/profiles/(.*)/awards/', AwardsClaimedForProfileFeed(),
        name="badge_feed_profileawards"),
    url(r'feeds/atom/badges/(.*)/awards/', AwardsClaimedForBadgeFeed(),
        name="badge_feed_badgeawards"),

    url(r'feeds/json/recentawards/', RecentlyClaimedAwardsJSONFeed(), 
        name="badge_json_recentawards"),
    url(r'feeds/json/profiles/(.*)/awards/', AwardsClaimedForProfileJSONFeed(),
        name="badge_json_profileawards"),
    url(r'feeds/json/badges/(.*)/awards/', AwardsClaimedForBadgeJSONFeed(),
        name="badge_json_badgeawards"),

)
