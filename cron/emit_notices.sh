#!/bin/sh
PROJECT_ROOT=`dirname $0`/..
cd $PROJECT_ROOT
python manage.py emit_notices
