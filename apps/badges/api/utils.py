"""
"""
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse
from piston.authentication import OAuthAuthentication, HttpBasicAuthentication

KEY_SIZE = 18
PASSWORD_SIZE = 32


class ValetKeyAuthentication(object):
    pass


class ValetKeyManager(models.Manager):
    pass


class ValetKey(models.Model):
    objects = ValetKeyManager()

    name = models.CharField(max_length=255)
    description = models.TextField()
    key = models.CharField(max_length=KEY_SIZE)
    password = models.CharField(max_length=PASSWORD_SIZE)
    user = models.ForeignKey(User, null=True, blank=True, related_name='valet_keys')
    

# See also: http://djangosnippets.org/snippets/1871/

class MultiValueHttpResponse(HttpResponse):
    '''
    A subclass of HttpResponse that is capable of representing multiple instances of a header.
    Use 'add_header_value' to set or add a value for a header.
    Use 'get_header_values' to get all values for a header.
    'items' returns an array containing each value for each header.
    'get' and '__getitem__' return the first value for the requested header.
    '__setitem__' replaces all values for a header with the provided value.
    '''
    def __init__(self, *args, **kwargs):
        super(MultiValueHttpResponse, self).__init__(*args, **kwargs)
        self._multi_value_headers = {}
        # the constructor may set some headers already
        for item in super(MultiValueHttpResponse, self).items():
            self[item[0]] = item[1]

    def __str__(self):
        return '\n'.join(['%s: %s' % (key, value)
                          for key, value in self.items()]) + '\n\n' + self.content
    
    def __setitem__(self, header, value):
        header, value = self._convert_to_ascii(header, value)
        self._multi_value_headers[header.lower()] = [(header, value)]

    def __getitem__(self, header):
        return self._multi_value_headers[header.lower()][0][1]

    def items(self):
        items = []
        for header_values in self._multi_value_headers.values():
            for entry in header_values:
                items.append((entry[0], entry[1]))

        return items

    def get(self, header, alternate):
        return self._multi_value_headers.get(header.lower(), [(None, alternate)])[0][1]

    def add_header_value(self, header, value):
        header, value = self._convert_to_ascii(header, value)
        lower_header = header.lower()
        if not lower_header in self._multi_value_headers:
            self._multi_value_headers[lower_header] = []
        self._multi_value_headers[lower_header].append((header, value))

    def get_header_values(self, header):
        header = self._convert_to_ascii(header)

        return [header[1] for header in self._multi_value_headers.get(header.lower(), [])]

class MultipleAuthentication(object):
    def __init__(self, **methods):
        self.methods = methods
    
    def is_authenticated(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header:
            return False

        (method, auth) = auth_header.split(" ", 1)
        if method in self.methods:
            return self.methods[method].is_authenticated(request)

        return False

    def challenge(self):
        response = MultiValueHttpResponse('Authorization Required',
                                          content_type="text/plain", status=401)
        for method in self.methods.values():
            challenge = method.challenge().get('WWW-Authenticate', None)
            if challenge:
                response.add_header_value('WWW-Authenticate', challenge)

        return response

API_AUTHENTICATION = MultipleAuthentication(Basic=HttpBasicAuthentication(),
                                            OAuth=OAuthAuthentication())
    
