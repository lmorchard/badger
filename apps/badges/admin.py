from django.contrib import admin

from badges.models import Badge, BadgeNomination, BadgeAward, BadgeAwardee

admin.site.register(Badge)
admin.site.register(BadgeNomination)
admin.site.register(BadgeAward)
admin.site.register(BadgeAwardee)
