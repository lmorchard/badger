from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from badger.apps.badges.models import Badge, BadgeNomination
from badger.apps.badges.models import BadgeAward, BadgeAwardee
from badger.apps.badges.forms import BadgeForm, BadgeNominationForm

from notification import models as notification


def index(request):
    """Browse badges"""
    badges = Badge.objects.all()

    return render_to_response('badges/index.html', {
        'badges': badges
    }, context_instance=RequestContext(request))


@login_required
def create(request):
    """Create a new badge"""
    if request.method == "POST":
        form = BadgeForm(request.POST)
        if form.is_valid():
            new_badge = form.save(commit=False)
            new_badge.creator = request.user
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


def badge_details(request, badge_slug):
    """Show details on a badge"""
    badge = get_object_or_404(Badge, slug=badge_slug)

    if request.method == "POST":

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

    else:
        nomination_form = BadgeNominationForm()

    nominations = BadgeNomination.objects.filter(badge=badge, approved=False)
    awards = BadgeAward.objects.filter(badge=badge)

    return render_to_response('badges/detail.html', {
        'badge': badge,
        'nomination_form': nomination_form,
        'nominations': nominations,
        'awards': awards
    }, context_instance=RequestContext(request))


def nomination_details(request, badge_slug, nomination_name):
    """Display details on a nomination"""
    badge = get_object_or_404(Badge, slug=badge_slug)

    try:
        validators.validate_email(nomination_name)
        nominee = get_object_or_404(BadgeAwardee, email=nomination_name)
    except ValidationError:
        nominee_user = User.objects.get(username__exact=nomination_name)
        nominee = get_object_or_404(BadgeAwardee, user=nominee_user)

    nomination = get_object_or_404(BadgeNomination, badge=badge,
            nominee=nominee)

    if request.method == "POST":
        if request.POST.get('action', None) == 'approve':
            new_award = nomination.approve(request.user)
            messages.add_message(
                request, messages.SUCCESS,
                ugettext("nomination approved for %s" % (new_award))
            )
            return HttpResponseRedirect(reverse(
                'badger.apps.badges.views.badge_details', args=(badge.slug,)
            ))

    return render_to_response('badges/nomination_detail.html', {
        'nomination': nomination
    }, context_instance=RequestContext(request))
