# -*- coding: utf-8 -*-
from django.db import models

class URLCount(models.Model):
    regex = models.TextField(unique=True)
    app_name = models.TextField(null=True, blank=True)
    number_of_calls = models.PositiveIntegerField(default=0)
    number_of_unmatched_calls = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return "r'%s', %d / %d" % (self.regex, self.number_of_calls, 
            self.number_of_unmatched_calls)            