"""
Utilities for publishing to supported services.
"""
import logging

import urllib, urllib2
from django.conf import settings
from django.utils import simplejson as json

from oauthtwitter import OAuthApi
from oauth import oauth
import oauthtwitter


class PublisherDoesNotExist(RuntimeError):
    """Generic exception class."""
    def __init__(self, message='Publisher does not exist'):
        self.message = message


class PublisherFailed(RuntimeError):
    """Generic exception class."""
    def __init__(self, message='Publisher failed to publish'):
        self.message = message


class BasePublisher:

    def publish(self, assoc, message, link_url, image_url, image_name, 
            image_description):
        logging.debug("PUBLISH %s ; %s ; %s ; %s" % (
            message, link_url, image_url, image_name
        ))
        pass


TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', 'YOUR_KEY')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', 'YOUR_SECRET')


class TwitterPublisher(BasePublisher):

    consumer_key = TWITTER_CONSUMER_KEY
    consumer_secret = TWITTER_CONSUMER_SECRET
    
    def publish(self, assoc, message, link_url, image_url, image_name, 
            image_description):
        try:
            access_token = oauth.OAuthToken.from_string(assoc.access_token)
            twitter = oauthtwitter.OAuthApi(
                self.consumer_key, self.consumer_secret, access_token
            )
            status = twitter.PostUpdate("%s %s" % (message, link_url))
        except Exception, e:
            # TODO: Better handling of failure cases (eg. 401)
            raise PublisherFailed()


class FacebookPublisher(BasePublisher):
    """Quick and dirty Facebook feed item publisher"""

    FEED_URL = "https://graph.facebook.com/me/feed"

    def publish(self, assoc, message, link_url, image_url, image_name, 
            image_description):
        try:
            access_token = assoc.access_token
            result = json.load(
                urllib2.urlopen(self.FEED_URL,
                    urllib.urlencode(dict(
                        access_token=access_token,
                        message=message,
                        picture=image_url,
                        link=link_url,
                        name=image_name,
                        caption=image_description
                    ))
                )
            )
            if type(result) is not dict:
                raise PublisherFailed("Response was not valid: %s" % result)
            if 'id' not in result:
                raise PublisherFailed("Response did not contain ID: %s" % result)
            # TODO: Cover more Facebook API failure cases
        except Exception, e:
            raise PublisherFailed()


publishers = {
    'twitter': TwitterPublisher(),
    'facebook': FacebookPublisher()
}


def publish(assoc, message, link_url, image_url, image_name, image_description):
    """Publish an item using one of the services."""
    type = assoc.auth_type
    if type not in publishers:
        raise PublisherDoesNotExist()
    return publishers[type].publish(
        assoc, message, link_url, image_url, image_name, image_description
    ) 
