# Badger v0.0

It might be nice to gift badges and track achievements for deserving people.

## Installation / Deployment

* Never been done, yet.

## FAQ

* Hasn't this been done before?
    * Yes, [at least once][bravonation] on the net.
* Why are you doing it, then?
    * Because I'd like to:
        1. Revive the idea; 
        2. Make it more generative and participatory;
        3. Introduce automated web-wide scanning for achievement conditions.
* Why's it all Comic Sans?
    * Because I want to annoy you into fixing it for me.
    * Also, because it's all still a prototype, and you shouldn't take it seriously yet.

## Hacking

I'll assume you're a bit of a Django hacker here, but this might help kick things off:

* Get the source from [github](http://github.com/lmorchard/badger).
    * (You're probably there now.)
* Make sure you have Python 2.4+, [pip][], and [virtualenv][].
    * I'm using Python 2.6.5 from MacPorts, for what it's worth.
* Follow the [Getting started guide for Pinax](http://pinaxproject.com/docs/dev/gettingstarted.html), mainly:
    * Use [virtualenv][] to create and use a new environment.
    * `pip install -r requirements/dev.txt`
    * `python manage.py syncdb`
    * `python manage.py runserver`
* If anything goes wrong, you're probably better informed than I am to fix it.

[virtualenv]: http://pypi.python.org/pypi/virtualenv
[pip]: http://pip.openplans.org/

## Credits & Influences

* Much inspiration from [BravoNation][] (R.I.P.)
* [Scouting Merit Badges](http://meritbadge.org/wiki/index.php/Main_Page) (ie. the originals)
* [Nerd Merit Badges](http://www.nerdmeritbadges.com/)
* [Badgers photo!](http://www.flickr.com/photos/66176388@N00/3955963781/)

[bravonation]: http://waxy.org/2007/12/exclusive_yahoo/
