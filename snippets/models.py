from __future__ import unicode_literals
# from django.db import models
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_all_styles
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.contrib.gis.db import models
from django.contrib.postgres.fields import HStoreField


LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


class Snippet(models.Model):
    created = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100, blank=True, default='')
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
    highlighted = models.TextField()
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        lexer= get_lexer_by_name(self.language)
        linenos = self.linenos and 'table' or False
        options = self.title and {'title':self.title} or {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title


class Location(models.Model):
    name = models.CharField(max_length=255)
    recieved = models.BooleanField(default=False)
    county = models.CharField(max_length=100)
    point = models.PointField(srid=4326)

    def __unicode__(self):
        return self.name


class Link(models.Model):
    """
    Metadata is stored in a PostgreSQL HStore field, which allows us to
    store arbitrary key-value pairs with a link record.
    """
    metadata = HStoreField(blank=True, null=True, default=dict)
    geo = models.LineStringField()
    objects = models.GeoManager()