import os.path

from django.conf import settings

try:
    from PIL import Image
except ImportError:
    import Image

AUTO_GENERATE_BADGE_SIZES = getattr(settings, 'AUTO_GENERATE_BADGE_SIZES', 
        (256,80,32,))
BADGE_RESIZE_METHOD = getattr(settings, 'BADGE_RESIZE_METHOD', Image.ANTIALIAS)
BADGE_STORAGE_DIR = getattr(settings, 'BADGE_STORAGE_DIR', 'badges')
BADGE_DEFAULT_URL = getattr(settings, 'BADGE_DEFAULT_URL', 
    settings.STATIC_URL + 'badges/img/default-badge.jpg')

from django.db.models import signals
from django.contrib.auth.models import User
from badges.models import Badge

def create_default_thumbnails(instance=None, created=False, **kwargs):
    if created:
        for size in AUTO_GENERATE_BADGE_SIZES:
            instance.create_thumbnail(size)

signals.post_save.connect(create_default_thumbnails, sender=Badge)
