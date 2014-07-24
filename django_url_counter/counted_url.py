# -*- coding: utf-8 -*-
import datetime
from django.utils import six
from django.conf import settings

from django.core.urlresolvers import (RegexURLPattern, RegexURLResolver, LocaleRegexURLResolver)

from models import URLCount

# Interval between writes to the database in seconds
INTERVAL = settings.get('URL_COUNTER_INTERVAL', 30)

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
    """
    Class that overwrites the resolve-function in order to collect statistics.
    """

    def __init__(self, *args, **kwargs):
        # Set up some variables needed for collecting the numbers
        self.access_counter = 0
        self.access_counter_not_matched = 0
        self.last_write = datetime.datetime.now()
        
        # Leave the rest to the superclass
        super(CountedRegexURLPattern, self).__init__(*args, **kwargs)
        
    def resolve(self, path):
        """
        Overwrite the resolve method and collect statistics
        """
        # Call the original resolve method    
        result = super(CountedRegexURLPattern, self).resolve(path)
        
        # Do the statistics collection part
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
    """
    Factory method for constructing URLRegexResolver and URLRegexURLPattern objects that
    replaces Django's url() method.
    """
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