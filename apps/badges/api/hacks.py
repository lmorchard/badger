"""Hacks to make the API work"""
import logging
log = logging.getLogger('nose.badger')

# Monkeypatch the piston app, because it tries parsing a JSON POST body as
# form-encoded params. That breaks oauth.

import piston.authentication
from oauth import oauth

def initialize_server_request(request):
    """
    HACK: (LMO) This is the point of the monkeypatch for piston, which attempts to
    only include parameters from a POST request if the request body can
    be parsed as parameters. (eg. JSON shouldn't bs parsed as params)
   
    See also: http://oauth.net/core/1.0/#rfc.section.9.1.1
    See also: http://getsatisfaction.com/oauth/topics/how_to_normalize_request_including_get_params_and_xml_body
    """
    include_post_body_as_params = ("POST" == request.method and (
        'multipart/form-data' in request.META['CONTENT_TYPE'] or 
        'application/x-www-form-urlencoded' in request.META['CONTENT_TYPE']
    ))
    if include_post_body_as_params: # Use merged GET and POST params.
        params = dict(request.REQUEST.items())
    else: # Just use GET params.
        params = dict(request.GET.items())

    # Seems that we want to put HTTP_AUTHORIZATION into 'Authorization'
    # for oauth.py to understand. Lovely.
    request.META['Authorization'] = request.META.get('HTTP_AUTHORIZATION', '')

    oauth_request = oauth.OAuthRequest.from_request(
        request.method, request.build_absolute_uri(), 
        headers=request.META, parameters=params,
        query_string=request.environ.get('QUERY_STRING', ''))

    if oauth_request:
        oauth_server = oauth.OAuthServer(piston.authentication.oauth_datastore(oauth_request))
        oauth_server.add_signature_method(oauth.OAuthSignatureMethod_PLAINTEXT())
        oauth_server.add_signature_method(oauth.OAuthSignatureMethod_HMAC_SHA1())
    else:
        oauth_server = None
        
    return oauth_server, oauth_request

piston.authentication.initialize_server_request = initialize_server_request
