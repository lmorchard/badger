# Badger v0.0

It might be nice to gift badges and track achievements for deserving people.

[I wrote a long article about the thinking and use cases behind this thing.](http://decafbad.com/2010/07/badger-article/)

## Installation / Deployment

* Never been done, yet.

## FAQ

* Hasn't this been done before?
    * Yes, many times.
* Why are you doing it, then?
    * Because I'd like to:
        1. Revive the idea; 
        2. Make it more generative and participatory;
        3. Introduce automated web-wide scanning for achievement conditions.

## Hacking

I'll assume you're a bit of a Django hacker here, but this might help kick things off:

* Get the source from [github](http://github.com/lmorchard/badger).
    * (You're probably there now.)
* Make sure you have Python 2.4+, [pip][], and [virtualenv][].
    * I'm using Python 2.6.5 from MacPorts, for what it's worth.
* Follow the [Getting started guide for Pinax](http://pinaxproject.com/docs/dev/gettingstarted.html), which is basically the following:
    * Use [virtualenv][] to create and use a new environment.
    * `pip install -r requirements/dev.txt`
    * `python manage.py syncdb`
    * `python manage.py migrate --all`
    * `python manage.py runserver`
* Using Freshen for tests, I've been using these commands:
    * `python manage.py test apps/badges --with-freshen`
        * This will run everything, including tests that fail because they're there to remind me of features to develop
    * `python -Wignore manage.py test apps/badges --with-freshen -v2 -lnose.badger --tags=~@TODO -a\!TODO`
        * This runs the Freshen feature tests, with log output enabled, and skips the scenarios tagged as @TODO as well as tests with a TODO attribute.
        * The `-Wignore` is to squelch a deprecation warning about md5 vs hashlib - should probably fix that some day.

[virtualenv]: http://pypi.python.org/pypi/virtualenv
[pip]: http://pip.openplans.org/

## Credits & Influences

* Much inspiration from [BravoNation][] (R.I.P.)
* [Scouting Merit Badges](http://meritbadge.org/wiki/index.php/Main_Page) (ie. the originals)
* [Nerd Merit Badges](http://www.nerdmeritbadges.com/)
* [Badgers photo!](http://www.flickr.com/photos/66176388@N00/3955963781/)
* <http://en.wikipedia.org/wiki/Wikipedia:Barnstars>
* <http://creative.mozilla.org/badges/>

[bravonation]: http://waxy.org/2007/12/exclusive_yahoo/
