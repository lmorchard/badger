"""Models for the badge application"""
import os
import os.path
import uuid
import random
from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string

from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from tagging.fields import TagField
from tagging.models import Tag

from notification import models as notification
from mailer import send_mail

from badger.apps.badges import BADGE_STORAGE_DIR, BADGE_RESIZE_METHOD

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image


# TODO: Does this need to be a setting?
RANDOM_CODE_LENGTH = 7


def badge_file_path(instance=None, filename=None, slug=None):
    slug = slug or instance.slug
    return os.path.join(BADGE_STORAGE_DIR, slug, filename)


class BadgeManager(models.Manager):
    def get_badges_for_user(self, user):
        return Badge.objects.raw("""
            SELECT *, count(badges_badgeaward.id) as award_count
            FROM badges_badgeawardee, badges_badgeaward, badges_badge
            WHERE 
                badges_badge.id = badges_badgeaward.badge_id AND
                badges_badgeaward.claimed = 1 AND
                badges_badgeaward.awardee_id = badges_badgeawardee.id AND
                badges_badgeawardee.user_id = %s
            GROUP BY
                badges_badge.id
            ORDER BY
                badges_badgeaward.updated_at DESC
        """, [user.id])


class Badge(models.Model):
    """Badge model"""
    objects = BadgeManager()

    title = models.CharField(_("title"), max_length=255,
        blank=False, unique=True)
    slug = models.SlugField(_("slug"), blank=False, unique=True)
    description = models.TextField(_("description"), blank=False)
    main_image = models.ImageField(_("main image"),
            max_length=1024, upload_to=badge_file_path, 
            blank=True, null=True,
            help_text=_('Main image for badge; should be square and 256x256 ' +
                    'or larger; will be automatically resized and cropped'))
    tags = TagField()
    autoapprove = models.BooleanField(_('Approve all nominations?'), 
        default=False, 
        help_text=_('If checked, all nominations will automatically be approved'))
    creator = models.ForeignKey(User, blank=False)
    creator_ip = models.IPAddressField(_("IP Address of the Creator"),
        blank=True, null=True)
    created_at = models.DateTimeField(_("created at"), default=datetime.now)
    updated_at = models.DateTimeField(_("updated at"))

    class Meta:
        unique_together = ('title','slug')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('badge_details', [self.slug]) 

    def allows_editing_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.creator:
            return True
        return False

    def allows_nomination_listing_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.creator:
            return True
        return False

    def thumbnail_exists(self, size):
        if not self.main_image or not self.main_image.name:
            return False
        return self.main_image.storage.exists(self.main_image_name(size))
    
    def create_thumbnail(self, size):
        try:
            orig = self.main_image.storage.open(self.main_image.name, 'rb').read()
            image = Image.open(StringIO(orig))
        except IOError:
            return # What should we do here?  Render a "sorry, didn't work" img?
        (w, h) = image.size
        if w != size or h != size:
            if w > h:
                diff = (w - h) / 2
                image = image.crop((diff, 0, w - diff, h))
            else:
                diff = (h - w) / 2
                image = image.crop((0, diff, w, h - diff))
            image = image.resize((size, size), BADGE_RESIZE_METHOD)
            if image.mode != "RGB":
                image = image.convert("RGB")
            thumb = StringIO()
            image.save(thumb, "JPEG")
            thumb_file = ContentFile(thumb.getvalue())
        else:
            thumb_file = ContentFile(orig)
        thumb = self.main_image.storage.save(self.main_image_name(size), thumb_file)
    
    def main_image_url(self, size=256):
        return self.main_image.storage.url(self.main_image_name(size))
    
    def main_image_name(self, size):
        return os.path.join(BADGE_STORAGE_DIR, self.slug,
            'resized', str(size), self.main_image.name)

    def nominate(self, nominator, nominee, reason_why):

        try:
            # If there's already a nomination for this badge + nominator +
            # nominee pending approval, treat this as an update.
            nomination = BadgeNomination.objects.filter(badge=self, 
                    nominator=nominator, nominee=nominee, 
                    approved=False).get()
        except BadgeNomination.DoesNotExist:
            # Otherwise, this is a new nomination.
            nomination = BadgeNomination()

        nomination.badge = self
        nomination.nominator = nominator
        nomination.nominee = nominee
        nomination.reason_why = reason_why
        nomination.save()

        if self.autoapprove:
            nomination.approve(self.creator)
        
        else:
            notes_to_send = [
                ( nominator, 'badge_nomination_sent'),
                ( self.creator, 'badge_nomination_proposed'),
            ]

            for note_to_send in notes_to_send:
                notification.send( 
                    [ note_to_send[0] ], note_to_send[1], 
                    { "nomination": nomination, "nominee": nominee }
                )

        return nomination

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.updated_at = datetime.now()
        super(Badge, self).save(**kwargs)


class BadgeAwardeeManager(models.Manager):
    """Manager additions to account for User-or-email queries"""

    def get_by_user_or_email(self, value):
        if type(value) is User:
            awardees = BadgeAwardee.objects.filter(user=value)
        else:
            awardees = BadgeAwardee.objects.filter(email=value)
        if not awardees:
            raise BadgeAwardee.DoesNotExist()
        return awardees[0]

    def get_or_create_by_user_or_email(self, value):
        try:
            return (self.get_by_user_or_email(value), False)
        except BadgeAwardee.DoesNotExist:
            if type(value) is User:
                awardee, created = BadgeAwardee.objects.get_or_create(user=value)
            else:
                awardee, created = BadgeAwardee.objects.get_or_create(email=value)
            return (awardee, created)


def make_random_code():
    s = '0123456789abcdefghijklmnopqrstuvwxyz'
    return ''.join([random.choice(s) for x in range(RANDOM_CODE_LENGTH)])


class BadgeAwardee(models.Model):
    """Representation of a someone awarded a badge, allows identifying people
    not yet signed up to the site by email address"""
    objects = BadgeAwardeeManager()

    claim_code = models.CharField(max_length=RANDOM_CODE_LENGTH,
            default=make_random_code, editable=False)
    user = models.ForeignKey(User, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        unique_together = ('user','email')

    def get_absolute_url(self):
        if self.user:
            return reverse("profile_detail", args=[self.user.username])
        elif self.email:
            return 'mailto:%s' % self.email

    def verify(self, user):
        """Claim this awardee identity for a given user, presumably in reaction
        to having been presented with the claim code."""

        if self.user and self.user != user:
            # Must be unverified or already verified as the given user.
            return False
        
        if not self.user:
            # Change the user for awardee if not already set.
            self.user = user

            # Send out notices for all unclaimed awards available to this awardee
            awards = BadgeAward.objects.filter(awardee=self).exclude(claimed=True)
            for award in awards:
                notification.send([self.user], 'badge_award_received', 
                        {"award": award})

        self.claim_code = make_random_code()
        self.save()

        return True

    def display(self):
        if self.user:
            return "%s" % self.user
        if self.email:
            return "%s" % self.email
        return "invalid awardee"

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
    reason_why = models.TextField(blank=False, default='')
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, null=True)
    approved_why = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(_("created at"), default=datetime.now)
    updated_at = models.DateTimeField(_("updated at"))

    class Meta:
        pass

    def __unicode__(self):
        return '%s nominated for %s' % (self.nominee, self.badge.title)

    @models.permalink
    def get_absolute_url(self):
        return ('badge_nomination', [self.badge.slug, self.id]) 

    def allows_viewing_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.badge.creator:
            return True
        if self.nominee.user and user == self.nominee.user:
            return True
        if user == self.nominator:
            return True
        return False

    def allows_approval_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.badge.creator:
            return True
        return False

    def allows_rejection_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.badge.creator:
            return True
        if self.nominee.user and user == self.nominee.user:
            return True
        if user == self.nominator:
            return True
        return False

    def approve(self, approved_by, reason_why=''):
        self.approved = True
        self.approved_by = approved_by
        self.save()

        new_award = BadgeAward(badge=self.badge, awardee=self.nominee,
                nomination=self)
        new_award.save()

        if notification:
            recipients = dict((x.username, x) for x in reversed((
                approved_by, self.nominator, self.badge.creator
            ))).values()
            notification.send(recipients, 'badge_awarded',
                    {"award": new_award})

        if notification and self.nominee.user:
            notification.send([self.nominee.user], 'badge_award_received',
                    {"award": new_award})

        elif self.nominee.email:
            context = {
                "award": new_award,
                "current_site": Site.objects.get_current()
            }
            subject = render_to_string(
                "badges/award_email_subject.txt", context)
            # remove superfluous line breaks
            subject = "".join(subject.splitlines())
            message = render_to_string(
                "badges/award_email_message.txt", context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                      [self.nominee.email], priority="high")

        return new_award

    def reject(self, rejected_by, reason_why=''):
        if notification:
            recipients = dict((x.username, x) for x in reversed((
                rejected_by, self.nominator, self.badge.creator
            ))).values()
            notification.send(recipients, 'badge_nomination_rejected', 
                    {'nomination': self, 'nominee': self.nominee,
                    'rejected_by': rejected_by, 'reason_why': reason_why})

        try:
            # Try deleting any existing award associated with this nomination
            existing_award = BadgeAward.objects.get(nomination=self)
            existing_award.delete()
        except BadgeAward.DoesNotExist:
            pass

        self.delete()

    def save(self, **kwargs):
        self.updated_at = datetime.now()
        super(BadgeNomination, self).save(**kwargs)


class BadgeAwardManager(models.Manager):
    def get_users_for_badge(self, badge):
        return User.objects.raw("""
            SELECT *, count(badges_badgeaward.id) as award_count
            FROM auth_user, badges_badgeawardee, badges_badgeaward, badges_badge
            WHERE 
                auth_user.id = badges_badgeawardee.user_id AND
                badges_badgeawardee.id = badges_badgeaward.awardee_id AND
                badges_badge.id = badges_badgeaward.badge_id AND
                badges_badgeaward.claimed = 1 AND
                badges_badge.id = %s
            GROUP BY
                auth_user.id
            ORDER BY
                badges_badgeaward.updated_at DESC
        """, [badge.id])


class BadgeAward(models.Model):
    """Representation of a badge awarded to a user"""
    objects = BadgeAwardManager()

    badge = models.ForeignKey(Badge)
    nomination = models.ForeignKey(BadgeNomination)
    awardee = models.ForeignKey(BadgeAwardee, verbose_name=_("awardee"))
    claimed = models.BooleanField(_('Award claimed?'), 
        default=False, help_text=_('If checked, the badge award is claimed.'))
    ignored = models.BooleanField(_('Award ignored?'), 
        default=False, help_text=_('If checked, the badge award is ignored.'))
    hidden = models.BooleanField(_('Badge hidden?'), 
        default=False, help_text=_('If checked, the badge award will be invisible.'))
    created_at = models.DateTimeField(_("created at"), default=datetime.now)
    updated_at = models.DateTimeField(_("updated at"))

    def __unicode__(self):
        return '%s awarded %s' % (self.awardee, self.badge.title)

    @models.permalink
    def get_absolute_url(self):
        return ('badge_award', [self.badge.slug, self.awardee, self.id]) 

    def save(self, **kwargs):
        self.updated_at = datetime.now()
        super(BadgeAward, self).save(**kwargs)

    def allows_viewing_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.awardee.user:
            return True
        if user == self.nomination.nominator:
            return True
        if user == self.badge.creator:
            return True
        if not self.claimed:
            return False
        if self.hidden:
            return False
        return True

    def allows_claim_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.awardee.user:
            return True
        return False

    def claim(self, whom_by):
        self.claimed = True
        self.save()

        if notification:
            recipients = dict((x.username, x) for x in reversed((
                self.awardee.user, self.nomination.nominator, 
                self.badge.creator
            ))).values()
            notification.send(recipients, 'badge_award_claimed', 
                    {"award": self})

    def reject(self, whom_by):
        if notification:
            recipients = dict((x.username, x) for x in reversed((
                self.awardee.user, self.nomination.nominator, 
                self.badge.creator
            ))).values()
            notification.send(recipients, 'badge_award_rejected', 
                    {"award": self})

        self.nomination.delete()
        self.delete()

    def ignore(self, whom_by):
        self.ignored = True
        self.save()

        if notification:
            recipients = dict((x.username, x) for x in reversed((
                self.awardee.user,
            ))).values()
            notification.send(recipients, 'badge_award_ignored', 
                    {"award": self})

    def hide(self):
        pass

    def show(self):
        pass


# handle notification of new comments
# from threadedcomments.models import ThreadedComment
# 
# 
# def new_comment(sender, instance, **kwargs):
#     post = instance.content_object
#     if isinstance(post, Badge):
#         if notification:
#             notification.send([post.author], "badge_comment",
#                 {"user": instance.user, "post": post, "comment": instance})
# 
# models.signals.post_save.connect(new_comment, sender=ThreadedComment)
