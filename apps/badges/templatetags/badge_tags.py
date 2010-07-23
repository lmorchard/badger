import urllib

from django import template
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils.hashcompat import md5_constructor

from badger.apps.badges import BADGE_DEFAULT_URL

register = template.Library()

def badge_url(badge, size=80):
    if badge.main_image is not None and badge.main_image.name is not None:
        if not badge.thumbnail_exists(size):
            badge.create_thumbnail(size)
        return badge.main_image_url(size)
    else:
        return BADGE_DEFAULT_URL
register.simple_tag(badge_url)

def badge_image(badge, size=80):
    alt = unicode(badge)
    url = badge_url(badge, size)
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (url, alt,
        size, size)
register.simple_tag(badge_image)

def render_badge(badge, size=80):
    return """<img src="%s" alt="%s" width="%s" height="%s" />""" % (
        badge.main_image_url(size), str(avatar), size, size)
register.simple_tag(render_badge)

