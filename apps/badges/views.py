from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext, ugettext_lazy as _

from django.contrib.auth.models import User
from badger.apps.badges.models import Badge, BadgeNomination, BadgeAward
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
                'badger.apps.badges.views.details', args=(new_badge.slug,)
            ))
    else:
        form = BadgeForm()

    return render_to_response('badges/create.html', {
        'form': form
    }, context_instance=RequestContext(request))

def details(request, badge_slug):
    """Show details on a badge"""
    badge = get_object_or_404(Badge, slug=badge_slug)

    if request.method == "POST":
        rv = _nominate_for_badge(request, badge)
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
    nominee = get_object_or_404(User, username=nomination_name)
    nomination = get_object_or_404(BadgeNomination, badge=badge, nominee=nominee)

    if request.method == "POST":
        
        new_award = BadgeAward(
            badge=badge, awardee=nomination.nominee, nomination=nomination
        )
        new_award.save()
        
        nomination.approved = True
        nomination.save()

        notification.send( 
            [ request.user, badge.creator, new_award.awardee ], 
            'badge_awarded', 
            { "award": new_award }
        )
        
        return HttpResponseRedirect(reverse(
            'badger.apps.badges.views.details', args=(badge.slug,)
        ))

    return render_to_response('badges/nomination_detail.html', {
        'nomination': nomination
    }, context_instance=RequestContext(request))

def _nominate_for_badge(request, badge):
    """Create/update a nomination for a user & badge"""
    nomination_form = BadgeNominationForm(request.POST)
    if not nomination_form.is_valid(): return False

    try:
        # Try to dig up an existing nomination for update.
        nominee_name = request.POST.get('nominee',None)
        nominee = User.objects.filter(username=nominee_name).get()
        old_nomination = BadgeNomination.objects.filter(
            badge=badge, nominator=request.user, nominee=nominee
        ).get()
    except BadgeNomination.DoesNotExist:
        # None existing, so just create a blank one.
        old_nomination = BadgeNomination()

    nomination_form = BadgeNominationForm(
        request.POST, instance=old_nomination
    )

    if not nomination_form.is_valid(): return False

    new_nomination = nomination_form.save(commit=False)
    new_nomination.badge = badge
    new_nomination.nominator = request.user
    new_nomination.save()

    messages.add_message(
        request, messages.SUCCESS, 
        ugettext("%s nominated for %s" % (new_nomination.nominee, badge))
    )

    notes_to_send = (
        ( request.user, 'badge_nomination_sent'),
        ( badge.creator, 'badge_nomination_proposed'),
        ( new_nomination.nominee, 'badge_nomination_received')
    )

    for note_to_send in notes_to_send:
        notification.send( [ note_to_send[0] ], note_to_send[1], {
            "nomination": new_nomination
        })

    return HttpResponseRedirect(reverse(
        'badger.apps.badges.views.details', args=(badge.slug,)
    ))

