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
from badger.apps.badges.models import Badge, BadgeNomination, BadgeAward, BadgeAwardee
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
                'badger.apps.badges.views.badge_details', args=(new_badge.slug,)
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
        rv = _nominate_for_badge(nomination_form, request, badge)
        if rv is not False: return rv
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
    
    nomination = get_object_or_404(BadgeNomination, badge=badge, nominee=nominee)

    if request.method == "POST" and request.POST.get('action', None) == 'approve':
        
        new_award = BadgeAward(badge=badge, awardee=nomination.nominee, 
            nomination=nomination)
        new_award.save()
        
        nomination.approved = True
        nomination.save()

        recipients = [ request.user, badge.creator ]
        if nominee.user:
            recipients.append(nominee.user)
        notification.send(recipients, 'badge_awarded', { "award": new_award })
        
        return HttpResponseRedirect(reverse(
            'badger.apps.badges.views.badge_details', args=(badge.slug,)
        ))

    return render_to_response('badges/nomination_detail.html', {
        'nomination': nomination
    }, context_instance=RequestContext(request))

def _nominate_for_badge(nomination_form, request, badge):
    """Create/update a nomination for a user & badge"""
    if not nomination_form.is_valid():
        return False

    nominee_value = nomination_form.cleaned_data['nominee']
    if type(nominee_value) is User:
        badge_awardee, created = BadgeAwardee.objects.get_or_create(user=nominee_value)
    else:
        badge_awardee, created = BadgeAwardee.objects.get_or_create(email=nominee_value)

    try:
        nomination = BadgeNomination.objects.filter(
            badge=badge, nominator=request.user, nominee=badge_awardee
        ).get()
    except BadgeNomination.DoesNotExist:
        nomination = BadgeNomination()

    nomination.badge = badge
    nomination.nominator = request.user
    nomination.nominee = badge_awardee
    nomination.reason_why = nomination_form.cleaned_data['reason_why']
    nomination.save()

    messages.add_message(
        request, messages.SUCCESS, 
        ugettext("%s nominated for %s" % (nomination.nominee, badge))
    )

    notes_to_send = [
        ( request.user, 'badge_nomination_sent'),
        ( badge.creator, 'badge_nomination_proposed'),
    ]

    if nomination.nominee.user:
        notes_to_send.append((nomination.nominee.user, 
            'badge_nomination_received'))

    for note_to_send in notes_to_send:
        notification.send( 
            [ note_to_send[0] ], note_to_send[1], 
            { "nomination": nomination }
        )

    return HttpResponseRedirect(reverse(
        'badger.apps.badges.views.badge_details', args=(badge.slug,)
    ))

