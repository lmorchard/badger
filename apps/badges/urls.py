from django.conf.urls.defaults import *
from badges.feeds import RecentlyClaimedAwardsFeed, RecentlyClaimedAwardsJSONFeed
from badges.feeds import AwardsClaimedForProfileFeed, AwardsClaimedForProfileJSONFeed
from badges.feeds import AwardsClaimedForBadgeFeed, AwardsClaimedForBadgeJSONFeed

urlpatterns = patterns("badger.apps.badges.views",
    url(r"^$", "index", name="badge_index"),
    url(r"^create$", "create", name="create_badge"),
    url(r"^badge/(.*)/nominations/(.*)$", "nomination_details", name="badge_nomination"),
    url(r"^verify/(.*)$", "awardee_verify", name="awardee_verify"),
    url(r"^badge/(.*)/awards/(.*)/$", "award_history", name="badge_award_list"),
    url(r"^badge/(.*)/awards/(.*)/showhide$", "award_show_hide_bulk", name="badge_award_show_hide"),
    url(r"^badge/(.*)/awards/(.*)/(.*)$", "award_details", name="badge_award"),
    url(r"^badge/(.*)/awards/(.*)/(.*)/showhide$", "award_show_hide_single", name="badge_award_show_hide_single"),
    url(r"^badge/(.*)/edit$", "edit", name="badge_edit"),
    url(r"^badge/(.*)$", "badge_details", name="badge_details"),

    url(r'feeds/atom/recentawards/', RecentlyClaimedAwardsFeed(), 
            name="badge_feed_recentawards"),
    url(r'feeds/atom/profiles/(.*)/awards/', AwardsClaimedForProfileFeed(),
            name="badge_feed_profileawards"),
    url(r'feeds/atom/badges/(.*)/awards/', AwardsClaimedForBadgeFeed(),
            name="badge_feed_badgeawards"),

    url(r'feeds/json/recentawards/', RecentlyClaimedAwardsJSONFeed(), 
            name="badge_json_recentawards"),
    url(r'feeds/json/profiles/(.*)/awards/', AwardsClaimedForProfileJSONFeed(),
            name="badge_feed_profileawards"),
    url(r'feeds/json/badges/(.*)/awards/', AwardsClaimedForBadgeJSONFeed(),
            name="badge_feed_badgeawards"),
)
