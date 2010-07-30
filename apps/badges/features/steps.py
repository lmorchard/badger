""" """
# -*- coding: utf-8 -*-

# TODO: Refactor this into separate step modules for web, badges, profiles

from freshen import *

import logging
import re
import urlparse
from lxml import etree
from pyquery import PyQuery
from django.test.client import Client
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from django.contrib.auth.models import User
from pinax.apps.profiles.models import Profile
from pinax.apps.account.models import Account
from badger.apps.badges.models import Badge, BadgeNomination
from badger.apps.badges.models import BadgeAward, BadgeAwardee
from mailer.models import Message, MessageLog
from notification.models import NoticeType, Notice

###########################################################################
# Hooks
###########################################################################

@Before
def before_all(sc):
    glc.log = logging.getLogger('nose.badger')
    scc.browser = Client()
    scc.last_response = None
    scc.current_path = None
    scc.current_page = None
    scc.current_form = None
    scc.current_form_context = None
    scc.context_email = None
    scc.context_url = None
    scc.name_path_map = {}

@After
def after_all(sc):
    pass

###########################################################################
# Step definitions
###########################################################################

@Given(u'in progress')
def given_todo():
    """Step indicating a feature under development, fails tests as a reminder"""
    ok_(False, 'TODO')

@Given(u'the "(.*)" page is at "(.*)"')
def establish_page_mapping(name, path):
    scc.name_path_map[name] = path

@Given(u'a user named "(.*)"')
def establish_user(username):
    user = get_user(username)

@Given(u'there are no existing badges')
def clear_badges_data():
    BadgeNomination.objects.all().delete()
    BadgeAward.objects.all().delete()
    BadgeAwardee.objects.all().delete()
    Badge.objects.all().delete()

@Given(u'I am logged in as "(.*)"')
def given_i_am_logged_in_as(username):
    user = get_user(username)
    succ = scc.browser.login(
        username=username, 
        password='%s_password' % username
    )
    ok_(succ, "login should succeed")

@Given(u'I am logged out')
def given_logged_out():
    scc.browser.logout()

@Given(u'I go to the "(.*)" page$')
def i_am_on_named_page(page_name):
    path = (page_name in scc.name_path_map and 
        scc.name_path_map[page_name] or page_name)
    page = visit_page(path)

@Given(u'"(.*)" creates a badge entitled "(.*)"')
def user_creates_badge(username, title):
    user = get_user(username)
    badge = Badge(
        title = title, 
        description = "Example description", 
        creator = user
    )
    badge.save()

@Given(u'the badge "(.*)" has "(.*)" set to "(.*)"')
def set_badge_prop(title, name, value):
    badge = Badge.objects.filter(title__exact=title).get()
    if value == 'True':
        value = True
    if value == 'False':
        value = False
    setattr(badge, name, value)
    badge.save()

@Given(u'I go to the "badge detail" page for "(.*)"')
def go_to_badge_detail_page(title):
    badge = Badge.objects.get(title__exact=title)
    path = '/badges/badge/%s' % badge.slug
    visit_page(path)

@Given(u'"(.*)" nominates "(.*)" for a badge entitled "(.*)" because "(.*)"')
def create_nomination(nominator_name, nominee_name, badge_title, badge_reason_why):
    badge = Badge.objects.get(title__exact=badge_title)
    nominator = User.objects.get(username__exact=nominator_name)
    try:
        validators.validate_email(nominee_name)
        nominee, created = BadgeAwardee.objects.get_or_create(email=nominee_name)
    except ValidationError:
        nominee_user = User.objects.get(username__exact=nominee_name)
        nominee, created = BadgeAwardee.objects.get_or_create(user=nominee_user)
    nomination = badge.nominate(nominator, nominee, badge_reason_why)

@Given(u'"(.*)" approves the nomination of "(.*)" for a badge entitled "(.*)" because "(.*)"')
def approve_nomination(approver_name, nominee_name, badge_title, reason_why):
    try:
        validators.validate_email(nominee_name)
        nominee, created = BadgeAwardee.objects.get_or_create(email=nominee_name)
    except ValidationError:
        nominee_user = User.objects.get(username__exact=nominee_name)
        nominee, created = BadgeAwardee.objects.get_or_create(user=nominee_user)
    approver = User.objects.get(username__exact=approver_name)
    badge = Badge.objects.get(title__exact=badge_title)
    nomination = BadgeNomination.objects.get(
            badge=badge, nominee=nominee)
    nomination.approve(approver, reason_why)

@Given(u'"(.*)" approves "(.*)"\'s nomination of "(.*)" for a badge entitled "(.*)" because "(.*)"')
def approve_exact_nomination(approver_name, nominator_name, nominee_name, badge_title, reason_why):
    approver_user = User.objects.get(username=approver_name)
    nominator_user = User.objects.get(username=nominator_name)
    nominee_user = User.objects.get(username=nominee_name)
    nominee = BadgeAwardee.objects.get(user=nominee_user)
    badge = Badge.objects.get(title__exact=badge_title)
    nomination = BadgeNomination.objects.get(badge=badge, 
            nominee=nominee, nominator=nominator_user)
    nomination.approve(approver_user, reason_why)

@When(u'I go to the "(.*)" page$')
def i_go_to_named_page(page_name):
    path = (page_name in scc.name_path_map and 
        scc.name_path_map[page_name] or page_name)
    page = visit_page(path)

@When(u'I reload the page')
def page_reload():
    page = visit_page(scc.current_path)

@When(u'I go to the "badge detail" page for "(.*)"')
def when_i_go_to_badge_detail_page(title):
    badge = Badge.objects.get(title__exact=title)
    path = '/badges/badge/%s' % badge.slug
    visit_page(path)

@When(u'I fill in "(.*)" with "(.*)"')
def fill_form_field(field_name, field_value):
    """Look for the named field and fill it"""
    page = scc.current_page
    ok_(scc.current_page is not None, "there should be a current page")
    
    # Try by direct name first.
    field = page('*[name="%s"]' % field_name)

    # Then, try by ID.
    if (len(field) == 0):
        field = page('#%s' % field_name)

    # Next, try by association with a label.
    if (len(field) == 0):
        label = page('label:contains("%s")' % field_name)
        if (len(label) == 1):
            field_name = label.attr('for')
            # Try the label's for attribute as either name or ID.
            field = page('*[name="%s"]' % field_name)
            if (len(field)==0):
                field = page('#%s' % field_name)

    ok_(len(field) == 1, 'the form field named/labelled "%s" should exist on %s' % (
        field_name, scc.current_path
    ))
    scc.current_form[field.attr('name')] = field_value

@When(u'I find the form containing "(.*)" in the "(.*)" section')
def find_context_form_by_section(context_content, section_title):
    section = find_section_in_page(section_title)
    form = section.find('form *:contains("%s")' % context_content).parents('form')
    ok_(len(form) > 0, "the form containing '%s' should be found" % context_content)
    scc.current_form_context = form
    return form

@When(u'I find the form containing "(.*)" somewhere on the page')
def find_context_form(context_content):
    page = scc.current_page
    form = page('form *:contains("%s")' % context_content).parents('form')
    ok_(len(form) > 0, "the form containing '%s' should be found" % context_content)
    scc.current_form_context = form
    return form

@When(u'I press "(.*)"')
def press_form_button(button_name):
    page = scc.current_page
    ok_(scc.current_page is not None, "there should be a current page")

    if scc.current_form_context is not None:
        # If we have a form context, search for the button within that form.
        form = scc.current_form_context
        form_action = form.attr('action')
        if not form_action: 
            form_action = scc.current_path
        form_method = form.attr('method')
        if not form_method: 
            form_method = 'post'

        field = form.find('input[value^="%s"]' % button_name)
        button_value = field.val()
        if len(field) == 0:
            field = form.find('button:contains("%s")' % button_name)
            button_value = field.text()
        if len(field) == 0:
            field = form.find('*[name="%s"]' % button_name)
            button_value = field.text()
        ok_(len(field) > 0, 'button "%s" should exist' % button_name)

        button_name = field.attr('name')
        scc.current_form[button_name] = button_value

    else:
        # If we have no form context, find the button and work up to the form.
        field = page('input[value^="%s"]' % button_name)
        button_value = field.val()
        if len(field) == 0:
            field = page('button:contains("%s")' % button_name)
            button_value = field.text()
        if len(field) == 0:
            field = page('*[name="%s"]' % button_name)
            button_value = field.text()
        ok_(len(field) > 0, 'button "%s" should exist' % button_name)

        button_name = field.attr('name')
        scc.current_form[button_name] = button_value

        form = field.parents('form:first')
        form_action = form.attr('action')
        if not form_action: 
            form_action = scc.current_path
        form_method = form.attr('method')
        if not form_method: 
            form_method = 'post'

    for field in form.find('input,textarea,select'):
        p_field = PyQuery(field)
        name, value = p_field.attr('name'), p_field.val()
        if value is None: value = ''
        if name not in scc.current_form:
            scc.current_form[name] = value

    if form_method.lower() == 'post':
        resp = scc.browser.post(form_action, scc.current_form, follow=True)
    else:
        resp = scc.browser.get(form_action, scc.current_form, follow=True)

    #eq_(200, resp.status_code)
    set_current_page(form_action, resp)

@When(u'I click on "(.*)" in the "(.*)" section')
def click_link_in_section(link_content, section_title):
    page = scc.current_page
    section = find_section_in_page(section_title)
    link = section.find('a.%s' % link_content)
    if len(link) == 0:
        link = section.find('*:contains("%s")' % link_content)
    ok_(len(link) > 0, 'link "%s" should be found in section "%s"' % (link_content, section_title))
    path = link.attr('href')
    page = visit_page(path)

@When(u'I go to the profile page for "(.*)"')
def visit_profile_page(user_name):
    visit_page(reverse('profile_detail', args=[user_name]))

@Then(u'I should see no form validation errors')
def should_see_no_form_validation_errors():
    error_fields = scc.current_page('.errorField')
    eq_(0, len(error_fields), 'there should be no error fields')
    eq_(0, len(scc.current_page('#errorMsg')), 'there should be no error msg')
    
@Then(u'I should see form validation errors')
def should_see_form_validation_errors():
    error_fields = scc.current_page('.errorField')
    cond = len(error_fields) > 0 or len(scc.current_page('#errorMsg')) > 0
    ok_(cond, 'there should be one or more error fields')

@Then(u'I should see a status code of "(.*)"')
def status_code_check(expected_code):
    eq_(int(expected_code), scc.last_response.status_code)

@Then(u'I should see "(.*)" somewhere on the page')
def should_see_page_content(expected_content):
    page_content = scc.last_response.content
    try:
        pos = page_content.index(expected_content)
    except ValueError:
        ok_(False, '"%s" should be found in page content' % expected_content)

@Then(u'I should not see "(.*)" anywhere on the page')
def should_see_not_page_content(expected_content):
    page_content = scc.last_response.content
    try:
        pos = page_content.index(expected_content)
        ok_(False, '"%s" should NOT be found in page content' % expected_content)
    except ValueError:
        pass

@Then(u'I should see "(.*)" somewhere in the "(.*)" section')
def section_content_check(expected_content, section_title):
    page = scc.current_page
    section = find_section_in_page(section_title)
    section_content = section.text()
    try:
        pos = section_content.index(expected_content)
    except ValueError:
        ok_(False, '"%s" should be found in content for section "%s"' % 
            (expected_content, section_title))

@Then(u'I should not see "(.*)" anywhere in the "(.*)" section')
def section_no_content_check(expected_content, section_title):
    page = scc.current_page
    section = find_section_in_page(section_title)
    section_content = section.text()
    try:
        pos = section_content.index(expected_content)
        ok_(False, '"%s" should not be found in content for section "%s"' %
            (expected_content, section_title))
    except ValueError:
        pass

@Then(u'I should see the "(.*)" section')
def section_present_check(section_title):
    page = scc.current_page
    try:
        section = find_section_in_page(section_title)
    except:
        ok_(False, 'did not find the "%s" section' % section_title)

@Then(u'I should not see the "(.*)" section')
def section_missing_check(section_title):
    page = scc.current_page
    try:
        section = find_section_in_page(section_title)
        if section:
            ok_(False, 'found the "%s" section' % section_title)
    except:
        pass

@Then(u'I should see a page entitled "(.*)"')
def should_see_page_title(expected_title):
    page = scc.current_page
    hit = page('title:contains("%s")' % expected_title)
    ok_(len(hit) > 0, '"%s" should be found in page title' % expected_title)

@Then(u'I should see a page whose title contains "(.*)"')
def page_title_should_contain(expected_title):
    page = scc.current_page
    hit = page('title:contains("%s")' % expected_title)
    cond = (len(hit) > 0)
    if not cond:
        glc.log.debug("PAGE PATH %s" % ( scc.current_path ))
        glc.log.debug("PAGE TITLE CONTENT %s" % ( scc.last_response.content ))
    ok_(cond, '"%s" should be found in page title' % expected_title)

@Then(u'there should be no badge "(.*)"')
def badge_missing_check(badge_title):
    try:
        badge = Badge.objects.get(title__exact=badge_title)
        ok_(False, 'the badge "%s" should not exist' % badge_title)
    except Badge.DoesNotExist:
        pass

@Then(u'"(.*)" should be nominated by "(.*)" for badge "(.*)" because "(.*)"')
def check_nomination(nominee_name, nominator_name, badge_title, badge_reason_why):
    
    try:
        validators.validate_email(nominee_name)
        nominee, created = BadgeAwardee.objects.get_or_create(email=nominee_name)
    except ValidationError:
        nominee_user = User.objects.get(username__exact=nominee_name)
        nominee, created = BadgeAwardee.objects.get_or_create(user=nominee_user)

    nominator = User.objects.get(username__exact=nominator_name)
    badge = Badge.objects.get(title__exact=badge_title)

    nomination = BadgeNomination.objects.filter(
        nominee=nominee, nominator=nominator, badge=badge,
    ).get()

    eq_(badge_reason_why, nomination.reason_why)

@Then(u'"(.*)" should not be nominated for the badge "(.*)"')
def check_not_nominated(nominee_name, badge_title):
    
    try:
        validators.validate_email(nominee_name)
        nominee, created = BadgeAwardee.objects.get_or_create(email=nominee_name)
    except ValidationError:
        nominee_user = User.objects.get(username__exact=nominee_name)
        nominee, created = BadgeAwardee.objects.get_or_create(user=nominee_user)

    badge = Badge.objects.get(title__exact=badge_title)

    try:
        nomination = BadgeNomination.objects.get(nominee=nominee, badge=badge)
        ok_(False, '"%s" should not be nominated for "%s"' % 
                (nominee_name, badge_title))
    except BadgeNomination.DoesNotExist:
        pass

@Then(u'"(.*)" should be awarded the badge "(.*)"')
def check_badge_award(awardee_name, badge_title):
    user = User.objects.get(username__exact=awardee_name)
    awardee, created = BadgeAwardee.objects.get_or_create(user=user)
    badge = Badge.objects.get(title__exact=badge_title)

    award = BadgeAward.objects.filter(
        awardee=awardee, badge=badge
    ).get()

@Then(u'"(.*)" should not be awarded the badge "(.*)"')
def check_no_badge_award(awardee_name, badge_title):
    user = User.objects.get(username__exact=awardee_name)
    awardee, created = BadgeAwardee.objects.get_or_create(user=user)
    badge = Badge.objects.get(title__exact=badge_title)

    try:
        award = BadgeAward.objects.get(awardee=awardee, badge=badge)
        ok_(False, '"%s" should not be awarded "%s"' % 
                (awardee_name, badge_title))
    except BadgeAward.DoesNotExist:
        pass

@Then(u'"(.*)" should have "(.*)" awards for the badge "(.*)"')
def count_awards(awardee_name, expected_count, badge_title):
    user = User.objects.get(username__exact=awardee_name)
    awardee, created = BadgeAwardee.objects.get_or_create(user=user)
    badge = Badge.objects.get(title__exact=badge_title)

    award_count = BadgeAward.objects.filter(awardee=awardee, badge=badge).count()
    eq_(int(expected_count), award_count)

@Then(u'"(.*)" should have "(.*)" unclaimed awards for the badge "(.*)"')
def count_unclaimed_awards(awardee_name, expected_count, badge_title):
    user = User.objects.get(username__exact=awardee_name)
    awardee, created = BadgeAwardee.objects.get_or_create(user=user)
    badge = Badge.objects.get(title__exact=badge_title)

    award_count = BadgeAward.objects.filter(awardee=awardee, badge=badge,
            claimed=False).count()
    eq_(int(expected_count), award_count)

@Then(u'"(.*)" should have "(.*)" claimed awards for the badge "(.*)"')
def count_claimed_awards(awardee_name, expected_count, badge_title):
    user = User.objects.get(username__exact=awardee_name)
    awardee, created = BadgeAwardee.objects.get_or_create(user=user)
    badge = Badge.objects.get(title__exact=badge_title)

    award_count = BadgeAward.objects.filter(awardee=awardee, badge=badge,
            claimed=True).count()
    eq_(int(expected_count), award_count)

@Then(u'"(.*)" should receive a "(.*)" notification')
def check_notifications(username, notification_name):
    try:
        notice_type = NoticeType.objects.filter(label__exact=notification_name).get()
    except NoticeType.DoesNotExist:
        notice_type = NoticeType.objects.filter(display__exact=notification_name).get()

    user = User.objects.filter(username__exact=username).get()
    notices = Notice.objects.notices_for(user).filter(notice_type=notice_type).all()
    ok_(len(notices) > 0)

@Then(u'"(.*)" should be sent a "(.*)" email')
def check_queued_email(to_addr, expected_subject):
    queued_msgs = Message.objects.filter(to_address__exact=to_addr,
            subject__contains=expected_subject).all()
    ok_(len(queued_msgs)>0, 'an email "%s" to "%s" should be logged' % 
            (expected_subject, to_addr))
    scc.context_email = queued_msgs[0]

@Then(u'the email should contain a URL')
def check_context_email_for_url():
    ok_(scc.context_email is not None, 'there should be a context email')
    str = scc.context_email.message_body
    # This only finds http URLs, but that's probably okay for now.
    urls = re.findall("(?P<url>https?://[^\s]+)", str)
    ok_(len(urls)>0, 'there should be at least one URL in the email')
    scc.context_url = urls[0]

from django.contrib.sites.models import Site
@When(u'I visit the URL')
def visit_context_url():
    curr_site = Site.objects.all()[0]
    path = scc.context_url.replace('http://%s' % curr_site.domain, '')
    visit_page(path)


###########################################################################
# Utility functions
###########################################################################

def get_user(username, password=None, email=None):
    """Get a user for the given username, creating it if necessary."""
    if password is None: password = '%s_password' % username
    if email is None: email = '%s@example.com' % username
    try:
        user = User.objects.get(username__exact=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username, email, password)
    ok_(user is not None, "user should exist")
    return user

def set_current_page(path, resp):
    
    if resp.redirect_chain:
        last = resp.redirect_chain.pop()
        path = last[0].replace('http://testserver','')

    scc.last_response = resp
    scc.current_path = path
    
    try:
        scc.current_page = PyQuery(resp.content)
    except:
        scc.current_page = None
    
    scc.current_form = {}
    return scc.current_page

def visit_page(path, data={}, follow=True, status_code=200, **extra):
    resp = scc.browser.get(path, follow=follow)
    return set_current_page(path, resp)

def find_section_in_page(section_title):
    page = scc.current_page
    section = page('.%s' % section_title)
    if len(section) == 0:
        section = page(':header:contains("%s")' % section_title).parent()
    ok_(len(section) > 0, "the section %s should be found" % section_title)
    return section

