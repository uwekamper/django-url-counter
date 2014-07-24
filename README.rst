==================
django-url-counter
==================

This is a project for the europython 2014 Hackathon on a Boat #ep14boat.


How to use
----------

In order to collect the statistics you need to change you ``urls.py`` file. 
Instead of import ``from django.conf.urls``, you need to import ``django_url_counter.counted_url``.

You can usually do this by changing

::

  from django.conf.urls import patterns, include, url

into

::  

  from django.conf.urls import patterns, include
  from django_url_counter.counted_url import counted_url as url

Then you can leave the definition of your ``urlpatterns`` untouched.

Configuration
-------------

Interval setting: You can change the interval in which data is written to the database

::
 
   URL_COUNTER_INTERVAL = 30
   
The interval is given in seconds and the default value is to 30 seconds between each write.