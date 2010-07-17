"""Models for the badge application"""
from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from django.contrib.auth.models import User

from tagging.fields import TagField
from tagging.models import Tag

from notification import models as notification

class Badge(models.Model):
    """Badge model"""
    title = models.CharField(_("title"), max_length=255, blank=False, unique=True)
    slug = models.SlugField(_("slug"), blank=False, unique=True)
    description = models.TextField(_("description"), blank=False)
    tags = TagField()
    creator = models.ForeignKey(User)
    creator_ip = models.IPAddressField(
        _("IP Address of the Creator"),
        blank = True, null = True
    )
    created_at = models.DateTimeField(_("created at"), default=datetime.now)
    updated_at = models.DateTimeField(_("updated at"))
    
    def __unicode__(self):
        return self.title
    
    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.updated_at = datetime.now()
        super(Badge, self).save(**kwargs)

class BadgeNomination(models.Model):
    """Representation of a user nominated to receive a badge"""
    badge = models.ForeignKey(Badge)
    nominee = models.ForeignKey(User, blank=False, related_name="nominee", verbose_name=_("nominee"))
    nominator = models.ForeignKey(User, related_name="nominator", verbose_name=_("nominator"))
    approved = models.BooleanField(default=False)
    reason_why = models.TextField(blank=False)
    created_at = models.DateTimeField(_("created at"), default=datetime.now)
    updated_at = models.DateTimeField(_("updated at"))

    def __unicode__(self):
        return '%s nominated for %s' % (self.nominee.username, self.badge.title)

    def save(self, **kwargs):
        self.updated_at = datetime.now()
        super(BadgeNomination, self).save(**kwargs)

class BadgeAward(models.Model):
    """Representation of a badge awarded to a user"""
    badge = models.ForeignKey(Badge)
    nomination = models.ForeignKey(BadgeNomination)
    awardee = models.ForeignKey(User, verbose_name=_("awardee"))
    created_at = models.DateTimeField(_("created at"), default=datetime.now)
    updated_at = models.DateTimeField(_("updated at"))

    def __unicode__(self):
        return '%s awarded %s' % (self.awardee.username, self.badge.title)

    def save(self, **kwargs):
        self.updated_at = datetime.now()
        super(BadgeAward, self).save(**kwargs)

# handle notification of new comments
from threadedcomments.models import ThreadedComment
def new_comment(sender, instance, **kwargs):
    post = instance.content_object
    if isinstance(post, Badge):
        if notification:
            notification.send([post.author], "badge_comment", {
                "user": instance.user,
                "post": post,
                "comment": instance
            })

models.signals.post_save.connect(new_comment, sender=ThreadedComment)
