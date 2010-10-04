"""
Template tags for socialconnect integration
"""

from django import template
from django.utils.translation import ugettext as _
from socialconnect.models import UserOauthAssociation

register = template.Library()

@register.tag(name="socialconnect_by_user")
def do_socialconnect_by_user(parser, token):
    """
    Look up a social service association for a user.

    {% socialconnect_by_user user for twitter as connect_twitter %}
    {% socialconnect_by_user user for facebook as connect_facebook %} 
    """
    bits = token.contents.split()
    if len(bits) != 6:
        msg = "'%s' tag takes exactly five arguments" % bits[0]
        raise template.TemplateSyntaxError(msg)
    if bits[2] != 'for':
        msg = "second argument to '%s' tag must be 'for'" % bits[0]
        raise template.TemplateSyntaxError(msg)
    if bits[4] != 'as':
        msg = "fourth argument to '%s' tag must be 'as'" % bits[0]
        raise template.TemplateSyntaxError(msg)
    return SocialconnectByUserNode(bits[1], bits[3], bits[5])

class SocialconnectByUserNode(template.Node):
    def __init__(self, user, auth_type, context_var):
        self.user = user
        self.auth_type = auth_type
        self.context_var = context_var

    def render(self, context):
        try:
            user = template.resolve_variable(self.user, context)
        except template.VariableDoesNotExist:
            return ''
        try:
            context[self.context_var] = UserOauthAssociation.objects.get(
                    user=user, auth_type=self.auth_type)
        except UserOauthAssociation.DoesNotExist:
            return''
        return ''

