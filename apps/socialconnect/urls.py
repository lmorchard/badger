from django.conf.urls.defaults import *

from socialconnect.views import TwitterAuthView, FacebookAuthView

urlpatterns = patterns("",
    (r"^twitter/", include(TwitterAuthView().urls)),
    (r"^facebook/", include(FacebookAuthView().urls)),
)
