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
    title = models.CharField(_("title"), max_length=255,
        blank=False, unique=True)
    slug = models.SlugField(_("slug"), blank=False, unique=True)
    description = models.TextField(_("description"), blank=False)
    tags = TagField()
    autoapprove = models.BooleanField(_('automatically approve nominations?'),
        default=False)
    creator = models.ForeignKey(User)
    creator_ip = models.IPAddressField(_("IP Address of the Creator"),
        blank=True, null=True)
    created_at = models.DateTimeField(_("created at"), default=datetime.now)
    updated_at = models.DateTimeField(_("updated at"))

    def __unicode__(self):
        return self.title

    def nominate(self, nominator, nominee, reason_why):
        try:
            nomination = BadgeNomination.objects.filter(badge=self, 
                    nominator=nominator, nominee=nominee).get()
        except BadgeNomination.DoesNotExist:
            nomination = BadgeNomination()

        nomination.badge = self
        nomination.nominator = nominator
        nomination.nominee = nominee
        nomination.reason_why = reason_why
        nomination.save()

        notes_to_send = [
            ( nominator, 'badge_nomination_sent'),
            ( self.creator, 'badge_nomination_proposed'),
        ]

        if nomination.nominee.user:
            notes_to_send.append((nomination.nominee.user, 
                'badge_nomination_received'))

        for note_to_send in notes_to_send:
            notification.send( 
                [ note_to_send[0] ], note_to_send[1], 
                { "nomination": nomination }
            )

        if self.autoapprove:
            nomination.approve(self.creator)

        return nomination

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.updated_at = datetime.now()
        super(Badge, self).save(**kwargs)


class BadgeAwardee(models.Model):
    """Representation of a someone awarded a badge, allows identifying people
    not yet signed up to the site by email address"""
    user = models.ForeignKey(User, null=True)
    email = models.EmailField(null=True)

    def __unicode__(self):
        if self.user:
            return "%s" % self.user
        if self.email:
            return "%s" % self.email
        return "invalid awardee"


class BadgeNomination(models.Model):
    """Representation of a user nominated to receive a badge"""
    badge = models.ForeignKey(Badge)
    nominee = models.ForeignKey(BadgeAwardee, blank=False,
        related_name="nominee", verbose_name=_("nominee"))
    nominator = models.ForeignKey(User, related_name="nominator",
        verbose_name=_("nominator"))
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, null=True)
    reason_why = models.TextField(blank=False)
    created_at = models.DateTimeField(_("created at"), default=datetime.now)
    updated_at = models.DateTimeField(_("updated at"))

    def __unicode__(self):
        return '%s nominated for %s' % (self.nominee.username,
                self.badge.title)

    def approve(self, approved_by):
        self.approved = True
        self.approved_by = approved_by
        self.save()

        new_award = BadgeAward(badge=self.badge, awardee=self.nominee,
                nomination=self)
        new_award.save()

        if notification:
            recipients = [approved_by, self.badge.creator]
            if self.nominee.user:
                recipients.append(self.nominee.user)
            notification.send(recipients, 'badge_awarded',
                    {"award": new_award})

        return new_award

    def save(self, **kwargs):
        self.updated_at = datetime.now()
        super(BadgeNomination, self).save(**kwargs)


class BadgeAward(models.Model):
    """Representation of a badge awarded to a user"""
    badge = models.ForeignKey(Badge)
    nomination = models.ForeignKey(BadgeNomination)
    awardee = models.ForeignKey(BadgeAwardee, verbose_name=_("awardee"))
    created_at = models.DateTimeField(_("created at"), default=datetime.now)
    updated_at = models.DateTimeField(_("updated at"))

    def __unicode__(self):
        return '%s awarded %s' % (self.awardee, self.badge.title)

    def save(self, **kwargs):
        self.updated_at = datetime.now()
        super(BadgeAward, self).save(**kwargs)


# handle notification of new comments
from threadedcomments.models import ThreadedComment


def new_comment(sender, instance, **kwargs):
    post = instance.content_object
    if isinstance(post, Badge):
        if notification:
            notification.send([post.author], "badge_comment",
                {"user": instance.user, "post": post, "comment": instance})

models.signals.post_save.connect(new_comment, sender=ThreadedComment)
