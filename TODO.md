# TODO

* See also
    * http://www.earnmojo.com/
    * http://getglue.com/ (stickers)
    * http://www.badgeville.com/

## v0.1

* Creative facelift!

* Tags for badges

* Comments on badges

* Karma? Applause? Mood?

* Pagination on badges page

* Localization
    * L10N support for the site itself
    * L10N for badge content... later?
        * Delaying it could result in duplicate badges with the same intent in different locales

* Meta-badges for auto-nomination
    * Attach a list of badges to a badge
    * Any user who has all of them gets auto-nominated for the meta-badge

* Social sharing
    * Facebook: badge display on profile page (Facebook app); share new badges as a Facebook update (Facebook Connect)
    * Ning: badge display on profile page (Ning app); share new badges as status updates; show newly granted badges on Ning homepage
    * Twitter: tweet your new badge
    * Gravatar / Signature creator: Generated image that includes that person's name and top badges. Can be downloaded for use in email signatures, blogs, websites.

* Invitation-only at launch?
    * A badge award constitutes an invite
    * auto-complete on emails somehow too?

* Delegation of nomination approval
    * Allow badge creator to flag others as co-creators / nomination approvers

* Allow transfer of badge ownership
    * Another user becomes the new creator

* Digest notifications of nominations for approval

* Anyone with this badge can also bestow this badge (eg. viral delegates)

* Register interest in claiming a badge
    * Produces a list in the API for scripts looking to track achievement progress

* API using valet keys and selective permissions
    * Valet key = HTTP basic auth user/pass
    * Simpler than OAuth
    * Easily disposable
    * Never enables account actions (eg. password change, etc)
    * Per-valet key logging and reports?
    * Should allow for simple external services that track conditions and trigger nominations

* Reduce SQL queries

## v0.2

* AJAXification
    * Sprinkle in more AJAX / hidden iframe / facebox magic for in-place submissions
    * Lightweight interactions

* Auto-complete on profile name for badge nomination form

* It would be nice to have an attractive theme for the Mozilla installation, and maybe as a default

* Non-listed badges for surprises

* Search-then-create

* L10N / I18N support for badge content

* OAuth access to API
    * For site-to-site access, allows for trusted verification of identity and badge awards?
    * Badge award verification could lead to badges that grant access / authority?

* Use template fragment caching in lots of places

* Make sure caching headers for proxy work?

* Use Cache Machine
    * <http://github.com/jbalogh/django-cache-machine>

## Future

* Hide / show individual awards?
    * Seems not as useful or crucial as hide/show of all awards for a badge.

* Associate other media types with badges
    * Videos, especially played as fanfare on award claim
    * Audio, as fanfare

* Links break when a badge is renamed, which also renames the slug.
    * Add a UUID / base-60 ID, use in notifications, redirect to slug?

* For award-by-email, if the email matches the verified email of an existing user, switch to the user rather than using the verification code system?

* Strip out more unused Pinax apps / features
    * No "friends" / "invites" from friends_app?
    * No "about" app?

* Extend award-by-email to also send verification URLs by IM / Twitter / etc

* Make subjects of emails more descriptive, so gmail doesn't pile them up into threads

* Switch from disclosing database IDs in URLs to UUIDs? 6-character {a-zA-Z0-9} strings?

* HTML5 badge image editor / composer
    * See also: http://news.deviantart.com/article/125373/
    * See also: http://pixie.strd6.com/
    * See also: http://wallpapers.foxkeh.com/en/
    * See also: http://hacks.mozilla.org/2010/02/an-html5-offline-image-editor-and-uploader-application/

* Autocomplete on user names for badge nomination

* Combined search-or-create interface for exploring badges?
    * See also quora.com and getsatisfaction.com
    * Useful for finding and settling on existing badges before creating an inadvertant variant

* Allow badger app to be more reusable by checking for installation of notification, etc?

* Wishlist of badges
