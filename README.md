# Badger v0.0

It might be nice to gift badges and track achievements for deserving people.

[I wrote a long article about the thinking and use cases behind this thing.](http://decafbad.com/2010/07/badger-article/)

## Development

Here's how to get started hacking on Badger. If you're deploying this to a live
server, skim the following and skip to the next section.

* Get the source from [github](http://github.com/lmorchard/badger).
    * (You're probably there now.)
* Make sure you have at least Python 2.4, [pip][], and [virtualenv][].
    * I'm using Python 2.6.5 from MacPorts, for what it's worth.
* Prepare a `settings_local.py` file:
    * `cp settings_local.py-dist-dev settings_local.py`
    * Local config tweaks go here.
    * As long as you're fine using a sqlite database for dev, there's nothing to do here yet.
* Follow the [Getting started guide for Pinax](http://pinaxproject.com/docs/dev/gettingstarted.html), which is basically the following:
    * Use [virtualenv][] to create and use a new environment.
    * `pip install -r requirements/dev.txt -r requirements/compiled.txt`
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

## Deployment tips

These are alterations to the development notes for use when deploying to a live LAMP server:

* To make things easier, there's a github repo containing all the pure Python requirements for Badger:
    * Clone this as a submodule under `vendor/`
        * <http://github.com/lmorchard/badger-lib>
    * This takes the place of using `pip` to install packages, including Pinax.
    * No need for `virtualenv` when using the vendor lib repo.
    * Use the OS package manager to install modules from `requirements/compiled.txt`
* Prepare a `settings_local.py` file:
    * `cp settings_local.py-dist-prod settings_local.py`
    * Assuming there's a MySQL DB, configure its details here.
    * SMTP and memcache servers are expected here, as well.
* Be sure to use both `syncdb` and `migrate --all` to prepare and update the database:
    * `python manage.py syncdb`
    * `python manage.py migrate --all`
* Configure Apache/mod_wsgi to use `wsgi/badger.wsgi`

## FAQ

* Hasn't this been done before?
    * Yes, many times.
* Why are you doing it, then?
    * Because I'd like to:
        1. Revive the idea; 
        2. Make it more generative and participatory;
        3. Introduce automated web-wide scanning for achievement conditions.

## Credits & Influences

* Much inspiration from [BravoNation][] (R.I.P.)
* [Scouting Merit Badges](http://meritbadge.org/wiki/index.php/Main_Page) (ie. the originals)
* [Nerd Merit Badges](http://www.nerdmeritbadges.com/)
* [Badgers photo!](http://www.flickr.com/photos/66176388@N00/3955963781/)
* <http://en.wikipedia.org/wiki/Wikipedia:Barnstars>
* <http://creative.mozilla.org/badges/>
* <http://www.reddit.com/help/awards>

[bravonation]: http://waxy.org/2007/12/exclusive_yahoo/
