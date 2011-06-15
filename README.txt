.. contents:: **Table of contents**

Tiny Log Analizer
=================

This project adds to your system a new utility command: ``tinylogan``. This utility only works with
Apache-like access HTTP log where the response time data is enabled.

To know how to do this, see `this blog post`__ or, in brief change the configuration of your log format
from something like::

    LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined

To this::

    LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %T/%D" combined

The log record will change to something like this::

    [31/Jan/2008:14:19:07 +0000] "GET / HTTP/1.1" 200 7918 ""
    ... "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20061201 Firefox/2.0.0.11 (Ubuntu-feisty)" 0/95491

__ http://www.ducea.com/2008/02/06/apache-logs-how-long-does-it-take-to-serve-a-request/ 

Seconds and microsends
----------------------

The utility only cares about microsends (`%D`) so you need to have Apache 2.

How to use
==========

Here the complete guide::

    Usage: tinylogan [options] logfile
    
    Simple bash utility for analyze HTTP access log with enabled response time
    
    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -v, --verbose         verbose output during log analysis
      -s SIZE, --size=SIZE  choose the number of record to store in every log
      -q, --keep-query      keep query strings in URLs instead of cutting them.
                            Using this an URL with different query string is treat
                            like different URLs.
      -i INCLUDE_REGEX, --include=INCLUDE_REGEX
                            a regexp expression that all URLs must match of will
                            be discarded. Can be called multiple times
      -e EXCLUDE_REGEX, --exclude=EXCLUDE_REGEX
                            a regexp expression that all URLs must not match of
                            will be discarded. Can be called multiple times
      --min-time=MIN_TIME_MILLIS
                            ignore all entries that require less than this amount
                            of millisecs
      --max-time=MAX_TIME_MILLIS
                            ignore all entries that require more than this amount
                            of millisecs
      --skip-timeperiod-start=SKIP_TIME_START
                            do not analyse records before the given time
      --skip-timeperiod-end=SKIP_TIME_END
                            do not analyse records later the given time
    
      Date filters:
        For those kind of filters you need to specify a date. You are free to
        use a specific date in the format dd/mmm/aaaa, like "24/May/2011", but
        also some keyword for relative date like "today", "yesterday",
        "tomorrow".
    
        --start-date=START_DATE
                            date where to start analyze and record
        --end-date=END_DATE
                            date where to end analyze and record
    
      Time filters:
        When a time is needed, you must enter it in the format hh:mm:ss or
        simply hh:mm, like "09:21:30" or "09:21". Those filter are used for
        skip record that are registered "too late at night" or "too early in
        the morning".

TODO
====

* modificator for relative dates (like ``yesterday-1``)
* default ``.tinylogan`` file in users home folder, with default options
* a way to ignore min and max value from mutiple record of a URL
* right now all records are stored in memory... obviously this is not the way to
  parse a potentially multiple-gigabyte-long-file

