import hashlib

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from badger.apps.badges.models import Badge, BadgeNomination
from badger.apps.badges.models import BadgeAward, BadgeAwardee
from badger.apps.badges.models import badge_file_path
from badger.apps.badges.forms import BadgeForm, BadgeNominationForm
from badger.apps.badges.forms import BadgeNominationDecisionForm
from notification import models as notification
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    """Browse badges"""
    badges = Badge.objects.all()

    return render_to_response('badges/index.html', {
        'badges': badges
    }, context_instance=RequestContext(request))

import pinax.apps.profiles.views
def profile(request, username, template_name="profiles/profile.html", 
        extra_context=None):
    user = get_object_or_404(User, username=username)
    awards = BadgeAward.objects.filter(awardee__user=user, claimed=True)
    return pinax.apps.profiles.views.profile(request, username, template_name, {
        "awards": awards
    })

@login_required
def create(request):
    """Create a new badge"""
    if request.method == "POST":
        form = BadgeForm(request.POST)
        if form.is_valid():
            new_badge = form.save(commit=False)
            new_badge.creator = request.user
            new_badge.slug = slugify(new_badge.title)
            if 'main_image' in request.FILES:
                path = badge_file_path(slug=new_badge.slug, 
                    filename=hashlib.md5(request.FILES['main_image'].name).hexdigest())
                new_badge.main_image = path
                new_file = new_badge.main_image.storage.save(path, 
                    request.FILES['main_image'])
            new_badge.save()
            return HttpResponseRedirect(reverse(
                'badger.apps.badges.views.badge_details',
                args=(new_badge.slug,)
            ))
    else:
        form = BadgeForm()

    return render_to_response('badges/create.html', {
        'form': form
    }, context_instance=RequestContext(request))

@login_required
def edit(request, badge_slug):
    badge = get_object_or_404(Badge, slug=badge_slug)

    perms = {
        'editing': badge.allows_editing_by(request.user)
    }

    if not perms['editing']:
        return HttpResponseForbidden(_('access denied'))

    if request.method == "POST":
        form = BadgeForm(request.POST, instance=badge)
        if form.is_valid():
            new_badge = form.save(commit=False)
            new_badge.creator = request.user
            new_badge.slug = slugify(new_badge.title)
            if 'main_image' in request.FILES:
                path = badge_file_path(slug=new_badge.slug, 
                    filename=hashlib.md5(request.FILES['main_image'].name).hexdigest())
                new_badge.main_image = path
                new_file = new_badge.main_image.storage.save(path, 
                    request.FILES['main_image'])
            new_badge.save()
            return HttpResponseRedirect(reverse(
                'badger.apps.badges.views.badge_details',
                args=(new_badge.slug,)
            ))
    else:
        form = BadgeForm(instance=badge)

    return render_to_response('badges/edit.html', {
        'form': form
    }, context_instance=RequestContext(request))

def badge_details(request, badge_slug):
    """Show details on a badge"""
    badge = get_object_or_404(Badge, slug=badge_slug)

    nomination_form = BadgeNominationForm()

    perms = {
        'editing': badge.allows_editing_by(request.user)
    }

    if request.method == "POST":

        if (request.user.is_authenticated and 
            request.POST.get('action_nominate', None) is not None):

            nomination_form = BadgeNominationForm(request.POST)
            nomination_form.context = {"badge": badge, "nominator": request.user}
            if nomination_form.is_valid():
                nominee_value = nomination_form.cleaned_data['nominee']
                badge_awardee, created = \
                    BadgeAwardee.objects.get_or_create_by_user_or_email(
                            nominee_value)
                nomination = badge.nominate(request.user, badge_awardee,
                        nomination_form.cleaned_data['reason_why'])

                messages.add_message(request, messages.SUCCESS,
                    ugettext("%s nominated for %s" % (nomination.nominee, badge)))

                return HttpResponseRedirect(reverse(
                    'badger.apps.badges.views.badge_details', args=(badge.slug,)))

    if not request.user.is_authenticated():
        nominations = None
    elif badge.allows_nomination_listing_by(request.user):
        # List all nominations for this badge
        nominations = BadgeNomination.objects.filter(badge=badge
                ).exclude(approved=True)
    else:
        # List only own nominations for this badge
        nominations = BadgeNomination.objects.filter(badge=badge, 
                nominator=request.user).exclude(approved=True)

    awards = BadgeAward.objects.filter(badge=badge, claimed=True)

    if not request.user.is_authenticated():
        unclaimed_awards = []
    else:
        unclaimed_awards = BadgeAward.objects.filter(claimed=False,
                ignored=False, badge=badge, awardee__user=request.user)

    return render_to_response('badges/badge_detail.html', {
        'badge': badge,
        'nomination_form': nomination_form,
        'nominations': nominations,
        'awards': awards,
        'permissions': perms,
        'unclaimed_awards': unclaimed_awards
    }, context_instance=RequestContext(request))

def nomination_details(request, badge_slug, nomination_id):
    """Display details on a nomination"""
    badge = get_object_or_404(Badge, slug=badge_slug)

    nomination = get_object_or_404(BadgeNomination, badge=badge, id=nomination_id)

    perms = {
        "viewing": nomination.allows_viewing_by(request.user),
        "approval": nomination.allows_approval_by(request.user),
        "rejection": nomination.allows_rejection_by(request.user)
    }

    if not perms['viewing']:
        return HttpResponseForbidden(_('access denied'))

    if request.method == "POST":

        do_jump = False
        decision_form = BadgeNominationDecisionForm(request.POST)

        if request.POST.get('action_approve', None) is not None:
            if not perms['approval']:
                return HttpResponseForbidden(_('access denied'))
            new_award = nomination.approve(request.user, 
                    request.POST.get('reason_why', ''))
            messages.add_message(
                request, messages.SUCCESS,
                ugettext("nomination approved for %s" % (new_award))
            )
            do_jump = True

        if decision_form.is_valid() and request.POST.get('action_reject', None) is not None:
            if not perms["rejection"]:
                return HttpResponseForbidden(_('access denied'))
            messages.add_message(
                request, messages.SUCCESS,
                ugettext("nomination rejected for %s" % (nomination))
            )
            nomination.reject(request.user, 
                    decision_form.cleaned_data['reason_why'])
            do_jump = 'badge'

        if do_jump is not False:
            if do_jump is True:
                jump_val = request.POST.get('jump', 'award')
            else:
                jump_val = do_jump
            if jump_val == 'badge':
                return HttpResponseRedirect(reverse('badge_details', 
                    args=(badge.slug,)))
            else:
                return HttpResponseRedirect(reverse('badge_nomination', 
                     args=(badge.slug, nomination.id,)))
    
    else:
        decision_form = BadgeNominationDecisionForm()

    return render_to_response('badges/nomination_detail.html', {
        'nomination': nomination,
        'decision_form': decision_form,
        'permissions': perms
    }, context_instance=RequestContext(request))

def award_details(request, badge_slug, awardee_name, award_id):
    """Display details on an award"""
    badge = get_object_or_404(Badge, slug=badge_slug)

    try:
        validators.validate_email(awardee_name)
        award = get_object_or_404(BadgeAward, badge=badge, id=award_id,
                awardee__email=awardee_name)
    except ValidationError:
        awardee_user = User.objects.get(username__exact=awardee_name)
        award = get_object_or_404(BadgeAward, badge=badge, id=award_id,
                awardee__user=awardee_user)

    perms = {
        "viewing": award.allows_viewing_by(request.user),
        "claim": award.allows_claim_by(request.user)
    }

    if not perms['viewing']:
        return HttpResponseForbidden(_('access denied'))

    if request.method == "POST":
        do_jump = False

        if award.claimed == False and award.allows_claim_by(request.user):
                
            if request.POST.get('action_claim_award', None) is not None:
                award.claim(request.user)
                messages.add_message(request, messages.SUCCESS,
                    _("badge award claimed"))
                do_jump = True
            
            elif request.POST.get('action_reject_award', None) is not None:
                award.reject(request.user)
                messages.add_message(request, messages.SUCCESS,
                    _("badge award rejected"))
                do_jump = "badge"

            elif request.POST.get('action_ignore_award', None) is not None:
                award.ignore(request.user)
                messages.add_message(request, messages.SUCCESS,
                    _("badge award ignored"))
                do_jump = True

        if do_jump is not False:
            if do_jump is True:
                jump_val = request.POST.get('jump', 'award')
            else:
                jump_val = do_jump
            if jump_val == 'badge':
                return HttpResponseRedirect(reverse('badge_details', 
                    args=(badge.slug,)))
            else:
                return HttpResponseRedirect(reverse('badge_award', 
                     args=(award.badge.slug, award.awardee.user.username, 
                     award.id,)))

    return render_to_response('badges/award_detail.html', {
        'badge': badge, 
        'award': award, 
        'awardee': award.awardee,
        'permissions': perms
    }, context_instance=RequestContext(request))

def award_list(request, badge_slug, awardee_name):
    return HttpResponse("LIST OF AWARDS")

@login_required
def awardee_verify(request, awardee_claim_code):
    """Accept verification of an awardee identity given a valid code""" 
    awardee = get_object_or_404(BadgeAwardee, claim_code=awardee_claim_code)
    if not awardee.verify(request.user):
        return HttpResponseForbidden(_('not yours'))
    
    awards = BadgeAward.objects.filter(awardee=awardee).exclude(claimed=True)
    if awards.count() == 1:
        messages.add_message(request, messages.SUCCESS,
            _("Award eligibility confirmed"))
        return HttpResponseRedirect(awards[0].get_absolute_url())
    elif awards.count() > 0:
        messages.add_message(request, messages.SUCCESS,
            _("Multiple awards confirmed, check your notifications."))

    return HttpResponseRedirect(reverse('notification_notices'))

