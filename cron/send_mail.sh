#!/bin/sh

WWW_HOME=/www/badger.decafbad.com
PROJECT_ROOT=$WWW_HOME/app/badger

. $WWW_HOME/env/bin/activate
cd $PROJECT_ROOT

python manage.py send_mail >> /www/badger.decafbad.com/logs/cron_mail.log 2>&1
