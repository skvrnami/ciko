from django.contrib import admin

from .models import Text, RssFeed, Highlight

admin.site.register(Text)
admin.site.register(RssFeed)
admin.site.register(Highlight)
