from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from tagging.models import TaggedItem
#from wiki.models import Article as WikiArticle

from pinax.apps.account.openid_consumer import PinaxConsumer
from pinax.apps.topics.models import Topic

handler500 = "pinax.views.server_error"

if settings.ACCOUNT_OPEN_SIGNUP:
    signup_view = "pinax.apps.account.views.signup"
else:
    signup_view = "pinax.apps.signup_codes.views.signup"


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {
        "template": "homepage.html",
    }, name="home"),

    (r"^badges/", include("badges.urls")),
    
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^account/signup/$", signup_view, name="acct_signup"),

    (r"^account/", include("pinax.apps.account.urls")),
    (r"^openid/(.*)", PinaxConsumer()),
    (r"^socialconnect/", include("socialconnect.urls")),
    (r"^bbauth/", include("pinax.apps.bbauth.urls")),
    (r"^authsub/", include("pinax.apps.authsub.urls")),
    (r"^notices/", include("notification.urls")),
    (r"^messages/", include("messages.urls")),
    (r"^announcements/", include("announcements.urls")),
    (r"^comments/", include("threadedcomments.urls")),
    (r"^robots.txt$", include("robots.urls")),
    (r"^i18n/", include("django.conf.urls.i18n")),
    (r"^admin/", include(admin.site.urls)),
    (r"^avatar/", include("avatar.urls")),
    (r"^flag/", include("flag.urls")),

    #(r"^profiles/", include("pinax.apps.profiles.urls")),
    url(r"^profiles/$", "pinax.apps.profiles.views.profiles", name="profile_list"),
    #url(r"^profiles/profile/(?P<username>[\w\._-]+)/$", "pinax.apps.profiles.views.profile", name="profile_detail"),
    url(r"^profiles/profile/(?P<username>[\w\._-]+)/$", "badges.views.profile", name="profile_detail"),
    url(r"^profiles/edit/$", "pinax.apps.profiles.views.profile_edit", name="profile_edit"),
    
)

tagged_models = (
    dict(title="Topics",
        query=lambda tag: TaggedItem.objects.get_by_model(Topic, tag),
    ),
)
tagging_ext_kwargs = {
    "tagged_models": tagged_models,
}

urlpatterns += patterns("",
    url(r"^tags/(?P<tag>.+)/(?P<model>.+)$", "tagging_ext.views.tag_by_model",
        kwargs=tagging_ext_kwargs, name="tagging_ext_tag_by_model"),
    url(r"^tags/(?P<tag>.+)/$", "tagging_ext.views.tag",
        kwargs=tagging_ext_kwargs, name="tagging_ext_tag"),
    url(r"^tags/$", "tagging_ext.views.index", name="tagging_ext_index"),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        (r"", include("staticfiles.urls")),
    )
