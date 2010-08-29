# -*- coding: utf-8 -*-
# Django settings for social pinax project.

import os
import sys
from os.path import abspath, dirname, join
from site import addsitedir
import os.path
import posixpath
import pinax

sys.path.insert(0, abspath(join(dirname(__file__), "libs")))
sys.path.insert(0, abspath(join(dirname(__file__), "vendor")))

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = "default"

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

INTERNAL_IPS = [
    "127.0.0.1",
]

ADMINS = [
    # ("Your Name", "your_email@domain.com"),
]

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "dev.db",                       # Or path to database file if using sqlite3.
        "USER": "",                             # Not used with sqlite3.
        "PASSWORD": "",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}


CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "US/Eastern"

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = "en"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/site_media/static/"

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "media"),
    os.path.join(PINAX_ROOT, "media", PINAX_THEME),
]

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = "o^9#(k-_+74na4ri(k_cj8u=z#5++v0hi-8+rx7b^d!9iik)41"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.load_template_source",
    "django.template.loaders.app_directories.load_template_source",
]

MIDDLEWARE_CLASSES = [
    #"django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.common.CommonMiddleware",
    #'piston.middleware.CommonMiddlewareCompatProxy',
    #'piston.middleware.ConditionalMiddlewareCompatProxy',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_openid.consumer.SessionConsumer",
    "django.contrib.messages.middleware.MessageMiddleware",
    "groups.middleware.GroupAwareMiddleware",
    "pinax.apps.account.middleware.LocaleMiddleware",
    "django.middleware.doc.XViewMiddleware",
    "pagination.middleware.PaginationMiddleware",
    "django_sorting.middleware.SortingMiddleware",
    "djangodblog.middleware.DBLogMiddleware",
    "pinax.middleware.security.HideSensistiveFieldsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.transaction.TransactionMiddleware",
    "django403.middleware.Django403Middleware",
    #"django.middleware.cache.FetchFromCacheMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATE_DIRS = [
    os.path.join(PROJECT_ROOT, "apps", "badges", "templates"),
    os.path.join(PROJECT_ROOT, "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "csrf_context.csrf",
    "django.contrib.messages.context_processors.messages",
    
    "pinax.core.context_processors.pinax_settings",
    "staticfiles.context_processors.static_url",
    
    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    "pinax.apps.account.context_processors.account",
    "messages.context_processors.inbox",
    "context_processors.combined_inbox_count",
]

COMBINED_INBOX_COUNT_SOURCES = [
    "messages.context_processors.inbox",
    "notification.context_processors.notification",
]

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.markup",
    
    "pinax.templatetags",
    
    # external
    "notification", # must be first
    "django_openid",
    "emailconfirmation",
    "django_extensions",
    "robots",
    "mailer",
    "messages",
    "announcements",
    "oembed",
    "pagination",
    "gravatar",
    "threadedcomments",
    "timezones",
    "tagging",
    "ajax_validation",
    "avatar",
    "flag",
    "uni_form",
    "django_sorting",
    "django_markup",
    "staticfiles",
    "debug_toolbar",
    "tagging_ext",
    "voting",
    
    # Pinax
    "pinax.apps.analytics",
    "pinax.apps.profiles",
    "pinax.apps.account",
    "pinax.apps.topics",
    "pinax.apps.threadedcomments_extras",
    "pinax.apps.voting_extras",
    
    # project
    "badges",
    "socialconnect",
]

# Play with adding third-party apps under South management here:
SOUTH_MIGRATION_MODULES = {
#     "topics": "migrations_local.topics",
#     "announcements": "migrations_local.announcements",
#     "avatar": "migrations_local.avatar",
#     "notification": "migrations_local.notification",
#     "tagging": "migrations_local.tagging",
#     "threadedcomments": "migrations_local.threadedcomments",
#     "flag": "migrations_local.flag",
#     "mailer": "migrations_local.mailer",
#     "messages": "migrations_local.messages",
#     "oembed": "migrations_local.oembed",
}

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

MARKUP_FILTER_FALLBACK = "none"
MARKUP_CHOICES = [
    ("restructuredtext", u"reStructuredText"),
    ("textile", u"Textile"),
    ("markdown", u"Markdown"),
    ("creole", u"Creole"),
]
WIKI_MARKUP_CHOICES = MARKUP_CHOICES

AUTH_PROFILE_MODULE = "profiles.Profile"
NOTIFICATION_LANGUAGE_MODULE = "account.Account"

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_UNIQUE_EMAIL = EMAIL_CONFIRMATION_UNIQUE_EMAIL = False

if ACCOUNT_EMAIL_AUTHENTICATION:
    AUTHENTICATION_BACKENDS = [
        "pinax.apps.account.auth_backends.EmailModelBackend",
    ]
else:
    AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
    ]

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG
CONTACT_EMAIL = "lorchard@mozilla.com"
SITE_NAME = "Badger"
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URLNAME = "home"

ugettext = lambda s: s
LANGUAGES = [
    ("en", u"English"),
]

# URCHIN_ID = "ua-..."

YAHOO_MAPS_API_KEY = "..."

class NullStream(object):
    def write(*args, **kwargs):
        pass
    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    "cloak_email_addresses": True,
    "file_insertion_enabled": False,
    "raw_enabled": False,
    "warning_stream": NullStream(),
    "strip_comments": True,
}

# if Django is running behind a proxy, we need to do things like use
# HTTP_X_FORWARDED_FOR instead of REMOTE_ADDR. This setting is used
# to inform apps of this fact
BEHIND_PROXY = False

FORCE_LOWERCASE_TAGS = True

WIKI_REQUIRES_LOGIN = True

# Uncomment this line after signing up for a Yahoo Maps API key at the
# following URL: https://developer.yahoo.com/wsregapp/
# YAHOO_MAPS_API_KEY = ""

AUTO_GENERATE_AVATAR_SIZES = (80,32,24,)

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

TWITTER_CONSUMER_KEY = "GET A KEY FROM http://twitter.com/oauth"
TWITTER_CONSUMER_SECRET = "GET A SECRET FROM http://twitter.com/oauth"

GOOGLE_FRIEND_CONNECT_CONSUMER_KEY = "GET A KEY FROM http://www.google.com/friendconnect/"
GOOGLE_FRIEND_CONNECT_CONSUMER_SECRET = "GET A KEY FROM http://www.google.com/friendconnect/"

FACEBOOK_CONSUMER_KEY = "GET A KEY FROM http://developers.facebook.com/setup"
FACEBOOK_CONSUMER_KEY = "GET A SECRET FROM http://developers.facebook.com/setup"

OAUTH_AUTH_VIEW = "piston.authentication.oauth_auth_view"
OAUTH_CALLBACK_VIEW = "badges.api.handlers.request_token_ready"

