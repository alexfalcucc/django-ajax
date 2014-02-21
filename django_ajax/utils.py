"""
Utils
"""
from __future__ import unicode_literals

import json

from django.conf import settings
from django.http.response import HttpResponseRedirectBase, HttpResponse
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.db.models.base import ModelBase


class LazyJSONEncoder(json.JSONEncoder):
    """
    A JSONEncoder subclass that handle querysets and models objects.
    Add how handle your type of object here to use when dump json

    """

    def default(self, obj):
        # handles HttpResponse and exception content
        if issubclass(type(obj), HttpResponseRedirectBase):
            return obj['Location']
        elif issubclass(type(obj), TemplateResponse):
            return obj.rendered_content
        elif issubclass(type(obj), HttpResponse):
            return obj.content
        elif issubclass(type(obj), Exception):
            if settings.DEBUG:
                message = traceback_exception()
                if message:
                    return message
            return force_text(obj)

        # this handles querysets and other iterable types
        try:
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)

        # this handlers Models
        if isinstance(obj.__class__, ModelBase):
            return force_text(obj)

        return super(LazyJSONEncoder, self).default(obj)


def traceback_exception():
    """
    Return traceback exception
    Includes some code from http://www.djangosnippets.org/snippets/650/

    """
    import sys
    import traceback

    exc_type, exc_info, tb = sys.exc_info()
    if exc_type:
        message = '%s\n%s\n\nTRACEBACK:\n' % (exc_type.__name__, exc_info)
        for tb in traceback.format_tb(tb):
            message += '%s\n' % tb
        return message

    return False


def serialize_to_json(data, *args, **kwargs):
    """
    A wrapper for simplejson.dumps with defaults as:

    cls=LazyJSONEncoder

    All arguments can be added via kwargs
    """
    kwargs['cls'] = kwargs.get('cls', LazyJSONEncoder)

    return json.dumps(data, *args, **kwargs)
