from django.contrib import admin

from badger.apps.badges.models import Badge, BadgeNomination, BadgeAward

admin.site.register(Badge)
admin.site.register(BadgeNomination)
admin.site.register(BadgeAward)
