from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext, ugettext_lazy as _

from badger.apps.badges.models import Badge, BadgeNomination
from badger.apps.badges.forms import BadgeForm, BadgeNominationForm

from notification import models as notification

def details(request, badge_slug):

    badge = get_object_or_404(Badge, slug__exact=badge_slug)

    if request.method == "POST":
        nomination_form = BadgeNominationForm(request.POST)
        if nomination_form.is_valid():

            new_nomination = nomination_form.save(commit=False)
            new_nomination.badge = badge
            new_nomination.nominator = request.user
            new_nomination.save()

            messages.add_message(
                request, messages.SUCCESS, 
                ugettext("%s nominated for %s" % 
                    (new_nomination.nominee, badge))
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
    else:
        nomination_form = BadgeNominationForm()

    return render_to_response('badges/detail.html', {
        'badge': badge,
        'nomination_form': nomination_form
    }, context_instance=RequestContext(request))


@login_required
def create(request):

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

