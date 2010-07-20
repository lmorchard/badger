from django.db.models import signals, get_app
from south.signals import post_migrate
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_noop as _

notification = get_app('notification')

def create_notice_types(app, created_models, verbosity, **kwargs):

    notification.create_notice_type(
        "badge_nomination_sent", 
        _("Badge Nomination Sent"), 
        _("you have sent a nomination for a badge")
    )

    notification.create_notice_type(
        "badge_nomination_received", 
        _("Badge Nomination Received"), 
        _("you have been nominated for a badge")
    )

    notification.create_notice_type(
        "badge_nomination_proposed", 
        _("Badge Nomination Proposed"), 
        _("someone has been nominated to receive a badge for which you are a decision maker")
    )

    notification.create_notice_type(
        "badge_nomination_rejected", 
        _("Badge Nomination Rejected"), 
        _("a decision maker for a badge has rejected a nomination for award")
    )

    notification.create_notice_type(
        "badge_awarded", 
        _("Badge Awarded"), 
        _("a badge has been awarded")
    )

    notification.create_notice_type(
        "badge_award_claimed", 
        _("Badge Award Claimed"), 
        _("a badge award has been claimed")
    )

    notification.create_notice_type(
        "badge_award_rejected", 
        _("Badge Award Rejected"), 
        _("a badge award has been rejected")
    )

    notification.create_notice_type(
        "badge_award_ignored", 
        _("Badge Award Ignored"), 
        _("a badge award has been ignored")
    )

signals.post_syncdb.connect(create_notice_types, sender=notification)
post_migrate.connect(create_notice_types, sender=notification)

