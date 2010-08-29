from django.core import context_processors
from django.utils import encoding, functional, html


def csrf(request):
    # Django does it lazy like this.  I don't know why.
    def _get_val():
        token = context_processors.csrf(request)['csrf_token']
        # This should be an md5 string so any broken Unicode is an attacker.
        try:
            return html.escape(unicode(token))
        except UnicodeDecodeError:
            return ''
    return {'csrf_token': functional.lazy(_get_val, unicode)()}
