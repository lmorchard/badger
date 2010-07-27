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


class AwardeeDisplayNode(template.Node):
    def __init__(self, awardee, as_var=None):
        self.awardee_var = template.Variable(awardee)
        self.as_var = as_var
    
    def render(self, context):
        awardee = self.awardee_var.resolve(context)
        display = awardee.display()
        if self.as_var:
            context[self.as_var] = display
            return ""
        return display


@register.tag(name="awardee_display")
def do_awardee_display(parser, token):
    """
    Example usage::
    
        {% awardee_display awardee %}
    
    or if you need to use in a {% blocktrans %}::
    
        {% awardee_display awardee as awardee_display}
        {% blocktrans %}you have sent {{ awardee_display }} a gift.{% endblocktrans %}
    
    """
    bits = token.split_contents()
    
    if len(bits) == 2:
        awardee = bits[1]
        as_var = None
    elif len(bits) == 4:
        awardee = bits[1]
        as_var = bits[3]
    else:
        raise template.TemplateSyntaxError("'%s' takes either two or four arguments" % bits[0])
    
    return AwardeeDisplayNode(awardee, as_var)

