"""Global terrain for all Lettuce features"""
# see also: http://lettuce.it/reference/terrain.html#terrain-py

from lettuce import *

@before.all
def before_all():
    print "Hello there!"
    print "Lettuce will start to run tests right now..."

@after.all
def after_all(total):
    print "Congratulations, %d of %d scenarios passed!" % (
        total.scenarios_ran,
        total.scenarios_passed
    )
    print "Goodbye!"

