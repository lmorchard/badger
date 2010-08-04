# TODO

## v0.1

* Feeds - JSON, Atom (activity streams?)

* Hide / show awards on profile page

* Non-listed badges for surprises

* Invitation-only at launch?

## v0.2

* Karma? Applause? Mood?

* Pagination on badges page?

* API using valet keys and checkbox capabilities
    * Valet key = HTTP basic auth user/pass
    * Easily disposable
    * Per-valet key logging and reports?
    * Should allow for simple external services that track conditions and trigger nominations

* Delegation of nomination approval

* Comments

* Tags

## v0.3

* It would be nice to have an attractive theme for the Mozilla installation, and maybe as a default

* Search-then-create

* L10N / I18N support for the site itself

* L10N / I18N support for badge content

* OAuth access to API
    * For site-to-site access, allows for trusted verification of identity and badge awards?
    * Badge award verification could lead to badges that grant access / authority?

## Future

* For award-by-email, if the email matches the verified email of an existing user, switch to the user rather than using the verification code system?

* Sprinkle in more AJAX / hidden iframe / facebox magic for in-place submissions

* Strip out more unused Pinax apps / features
    * No "friends" / "invites" from friends_app?
    * No "about" app?

* Extend award-by-email to also send verification URLs by IM / Twitter / etc

* Make subjects of emails more descriptive, so gmail doesn't pile them up into threads

* Switch from disclosing database IDs in URLs to UUIDs? 6-character {a-zA-Z0-9} strings?

* HTML5 badge image editor / composer
    * See also: http://wallpapers.foxkeh.com/en/
    * See also: http://hacks.mozilla.org/2010/02/an-html5-offline-image-editor-and-uploader-application/

* Autocomplete on user names for badge nomination

* Combined search-or-create interface for exploring badges?
    * See also quora.com and getsatisfaction.com
    * Useful for finding and settling on existing badges before creating an inadvertant variant

* Allow badger app to be more reusable by checking for installation of notification, etc?

* Wishlist of badges

* Find a more abstract way to implement permissions in models, instead of allows_* methods and permissions dict in controller
    * At least move the perms dict construction into model
