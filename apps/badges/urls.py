from django.conf.urls.defaults import *

urlpatterns = patterns("badger.apps.badges.views",
    #url(r"^$", "friends_app.views.friends", name="invitations"),
    #url(r"^contacts/$", "friends_app.views.contacts",  name="invitations_contacts"),
    #url(r"^accept/(\w+)/$", "friends_app.views.accept_join", name="friends_accept_join"),
    url(r"^$", "index", name="badge_index"),
    url(r"^create$", "create", name="create_badge"),
    url(r"^details/(.*)/nominations/(.*)$", "nomination_details", name="badge_nomination"),
    url(r"^details/(.*)$", "details", name="badge_details"),
)

