#!/bin/bash
# This script should run from inside Hudson

cd $WORKSPACE
VENV=$WORKSPACE/venv

echo "Starting build..."

# Clean up after last time.
find . -name '*.pyc' | xargs rm

if [ ! -d "$VENV/bin" ]; then
    echo "No virtualenv found; making one..."
    virtualenv --no-site-packages $VENV
fi

source $VENV/bin/activate

pip install -qr requirements/dev.txt

cat > settings_local.py <<SETTINGS
import logging
from settings import *
LOG_LEVEL = logging.ERROR
INSTALLED_APPS += [ "django_nose", ]
SOUTH_TESTS_MIGRATE = False
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
CACHE_BACKEND = 'locmem://'
MAILER_EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
SETTINGS

echo "Starting tests..."
export FORCE_DB=1
coverage run manage.py test apps/badges --noinput --with-freshen --with-xunit --tags=~@TODO -a\!TODO
coverage xml $(find apps libs -name '*.py')

echo 'Mushroom mushroom!'
