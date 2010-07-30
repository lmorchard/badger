from django.conf.urls.defaults import *

urlpatterns = patterns("badger.apps.badges.views",
    url(r"^$", "index", name="badge_index"),
    url(r"^create$", "create", name="create_badge"),
    url(r"^badge/(.*)/nominations/(.*)$", "nomination_details", name="badge_nomination"),
    url(r"^badge/(.*)/awards/(.*)/(.*)$", "award_details", name="badge_award"),
    url(r"^verify/(.*)$", "awardee_verify", name="awardee_verify"),
    url(r"^badge/(.*)/awards/(.*)/$", "award_list", name="badge_award_list"),
    url(r"^badge/(.*)/edit$", "edit", name="badge_edit"),
    url(r"^badge/(.*)$", "badge_details", name="badge_details"),
)
