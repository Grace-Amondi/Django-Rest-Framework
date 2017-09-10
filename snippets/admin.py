# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Snippet,Location,Link

admin.site.register(Snippet)
admin.site.register(Location)
admin.site.register(Link)



