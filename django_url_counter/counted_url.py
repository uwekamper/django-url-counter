# -*- coding: utf-8 -*-
import datetime
from django.utils import six
from django.core.urlresolvers import (RegexURLPattern, RegexURLResolver, LocaleRegexURLResolver)

from models import URLCount

# Interval between writes to the database in seconds
INTERVAL = 10

def write_to_db(regex, app_name, number_of_calls, number_of_unmatched_calls):
    entry, created = URLCount.objects.get_or_create(regex=regex, app_name=app_name)
    entry.number_of_calls += number_of_calls
    entry.number_of_unmatched_calls += number_of_unmatched_calls
    entry.save()

class CountedRegexURLResolver(RegexURLResolver):
    
    def __init__(self, *args, **kwargs):
        self.access_counter = 0
        self.access_counter_not_matched = 0
        super(CountedRegexURLResolver, self).__init__(*args, **kwargs)
    
    def resolve(self, path):
        print "#### Resolving URLResolver %s, regex: %s" % (path, self.regex.pattern)
        result = super(CountedRegexURLResolver, self).resolve(path)
        return result
        
class CountedRegexURLPattern(RegexURLPattern):

    def __init__(self, *args, **kwargs):
        self.access_counter = 0
        self.access_counter_not_matched = 0
        self.last_write = datetime.datetime.now()
        super(CountedRegexURLPattern, self).__init__(*args, **kwargs)
        
    def resolve(self, path):
        result = super(CountedRegexURLPattern, self).resolve(path)
        self.access_counter += 1
        if result is None:
            self.access_counter_not_matched += 1
        now = datetime.datetime.now()
        if (now - self.last_write).seconds > INTERVAL:
            self.last_write = now
            write_to_db(self.regex.pattern, None, self.access_counter, self.access_counter_not_matched)
            self.access_counter = 0
            self.access_counter_not_matched = 0
        return result
        

def counted_url(regex, view, kwargs=None, name=None, prefix=''):
    if isinstance(view, (list,tuple)):
        # For include(...) processing.
        urlconf_module, app_name, namespace = view
        return CountedRegexURLResolver(regex, urlconf_module, kwargs, app_name=app_name, namespace=namespace)
    else:
        if isinstance(view, six.string_types):
            if not view:
                raise ImproperlyConfigured('Empty URL pattern view name not permitted (for pattern %r)' % regex)
            if prefix:
                view = prefix + '.' + view
        return CountedRegexURLPattern(regex, view, kwargs, name)