""" """
# -*- coding: utf-8 -*-
from freshen import *

import logging
from lxml import etree
from pyquery import PyQuery
from django.test.client import Client
from nose.tools import assert_equal, with_setup, assert_false, eq_, ok_
from django.contrib.auth.models import User
from pinax.apps.profiles.models import Profile
from pinax.apps.account.models import Account
from badger.apps.badges.models import Badge, BadgeNomination, BadgeAward
from notification.models import NoticeType, Notice

@Before
def before_all(sc):
    glc.log = logging.getLogger('nose.badger')
    scc.browser = Client()
    scc.last_response = None
    scc.current_path = None
    scc.current_page = None
    scc.current_form = None

@After
def after_all(sc):
    pass

###########################################################################
# Step definitions
###########################################################################

@Given(u'a user named "(.*)"')
def establish_user(username):
    user = get_user(username)

@Given(u'I am logged in as "(.*)"')
def given_i_am_logged_in_as(username):
    user = get_user(username)
    succ = scc.browser.login(
        username=username, 
        password='%s_password' % username
    )
    ok_(succ, "login should succeed")

name_path_map = {
    "create badge": "/badges/create"
}

@Given(u'I go to the "(.*)" page')
def i_am_on_named_page(page_name):
    path = (page_name in name_path_map and 
        name_path_map[page_name] or page_name)
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

@Given(u'I go to the badge detail page for "(.*)"')
def go_to_badge_detail_page(title):
    badge = Badge.objects.get(title__exact=title)
    path = '/badges/details/%s' % badge.slug
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
    glc.log.debug("Found field %s - %s" % (field.attr('name'), field))
    scc.current_form[field.attr('name')] = field_value

@When(u'I press "(.*)"')
def press_form_button(button_name):
    page = scc.current_page
    ok_(scc.current_page is not None, "there should be a current page")

    field = page('input[value="%s"]' % button_name)
    glc.log.debug("Found button by value %s - %s" % (button_name, field))

    form = field.parents('form:first')
    form_action = form.attr('action')
    if not form_action: 
        form_action = scc.current_path
    form_method = form.attr('method')
    if not form_method: 
        form_method = 'post'

    scc.current_form['csrfmiddlewaretoken'] = \
        page('input[name=csrfmiddlewaretoken]').val()

    if form_method == 'post':
        resp = scc.browser.post(form_action, scc.current_form, follow=True)
    else:
        resp = scc.browser.get(form_action, scc.current_form, follow=True)

    eq_(200, resp.status_code)
    set_current_page(form_action, resp)

@Then(u'I should see no form validation errors')
def should_see_no_form_validation_errors():
    page = scc.current_page
    error_lists = page('ul.errorlist')
    eq_(0, len(error_lists), 'there should be no error lists')
    
@Then(u'I should see "(.*)" somewhere on the page')
def should_see_page_content(expected_content):
    page_content = scc.last_response.content
    try:
        pos = page_content.index(expected_content)
    except ValueError:
        glc.log.debug("Page content: %s" % scc.last_response.content)
        ok_(False, '"%s" should be found in page content' % expected_content)

@Then(u'I should see a page entitled "(.*)"')
def should_see_page_title(expected_title):
    page = scc.current_page
    hit = page('title:contains("%s")' % expected_title)
    ok_(len(hit) > 0, '"%s" should be found in page title' % expected_title)

@Then(u'"(.*)" should be nominated by "(.*)" for badge "(.*)" because "(.*)"')
def check_nomination(nominee_name, nominator_name, badge_title, badge_reason_why):
    nominee = User.objects.get(username__exact=nominee_name)
    nominator = User.objects.get(username__exact=nominator_name)
    badge = Badge.objects.get(title__exact=badge_title)

    nomination = BadgeNomination.objects.filter(
        nominee__exact=nominee,
        nominator__exact=nominator,
        badge__exact=badge,
    ).get()

    eq_(badge_reason_why, nomination.reason_why)

@Then(u'"(.*)" should receive a "(.*)" notification')
def check_notifications(username, notification_name):
    try:
        notice_type = NoticeType.objects.filter(label__exact=notification_name).get()
    except NoticeType.DoesNotExist:
        notice_type = NoticeType.objects.filter(display__exact=notification_name).get()

    user = User.objects.filter(username__exact=username).get()
    notices = Notice.objects.notices_for(user).filter(notice_type__exact=notice_type)

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
    scc.last_response = resp
    scc.current_path = path
    scc.current_page = PyQuery(resp.content)
    scc.current_form = {}
    return scc.current_page

def visit_page(path, data={}, follow=True, status_code=200, **extra):
    resp = scc.browser.get(path)
    glc.log.debug("Visiting path %s with status %s" % (path, resp.status_code))
    eq_(status_code, resp.status_code)
    return set_current_page(path, resp)
