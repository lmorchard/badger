from django.conf.urls.defaults import *

from socialconnect.views import ManagementView, TwitterAuthView, FacebookAuthView

urlpatterns = patterns("",
    (r"^manage/", include(ManagementView().urls)),
    (r"^twitter/", include(TwitterAuthView().urls)),
    (r"^facebook/", include(FacebookAuthView().urls)),
)
