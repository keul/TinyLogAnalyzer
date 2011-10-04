.. contents:: **Table of contents**

Introduction
============

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

The utility only cares about microsends (`%D`) so you need to have `Apache 2`__.

__ http://httpd.apache.org/docs/

How to use
==========

Here the complete help::

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
                            a regexp expression that an URLs must match of will be
                            discarded. Can be called multiple times, expanding the
                            set
      -e EXCLUDE_REGEX, --exclude=EXCLUDE_REGEX
                            a regexp expression that an URLs must not match of
                            will be discarded. Can be called multiple times,
                            reducing the set
      --skip-day=SKIP_DAY   A regexp that repr specific whole day or a set of
                            dates that must be ignored. Can be called multiple
                            times
      --min-time=MIN_TIME_MILLIS
                            ignore all entries that require less than this amount
                            of millisecs
      --max-time=MAX_TIME_MILLIS
                            ignore all entries that require more than this amount
                            of millisecs
      --min-times=MIN_TIMES
                            set a minimum number of times that a entry must be
                            found to be used in the "Top average time" statistic
    
      Date filters:
        For those kind of filters you need to specify a date. You are free to
        use a specific date in the format dd/mmm/aaaa, like "24/May/2011", but
        also some keywords for relative date like "today", "yesterday",
        "tomorrow", "week" and "month". Use of "week" and "month" mean
        referring to first day of the current week or month. You can also
        provide a numerical modifier using "+" or "-" followed by a day
        quantity (example: "week-5" for going back of 5 days from the start of
        the week).
    
        --start-date=START_DATE
                            date where to start analyze and record
        --end-date=END_DATE
                            date where to end analyze and record
    
      Time filters:
        When a time is needed, you must enter it in the format hh:mm:ss or
        simply hh:mm, like "09:21:30" or "09:21". Those filter are used for
        skip record that are registered "too late at night" or "too early in
        the morning".
    
        --skip-timeperiod-start=SKIP_TIME_START
                            do not analyse records before the given time
        --skip-timeperiod-end=SKIP_TIME_END
                            do not analyse records later the given time
    
      Default configuration profiles:
        You can read a set of default configuration options from a
        ".tinylogan" file placed in the user's home directory. If this file is
        found, parameters from the "DEFAULT" section are read, but you can
        also add other sections. You can always override those options from
        the command line.
    
        -c PROFILE          read a different profile section than DEFAULT
        -U                  Ignore the user default profile file (if exists)
        --example-profile   Print out an example profile file, then exit. You can
                            put this output in a ".tinylogan" file in your home,
                            then customize it

You can also configure your defaults values in a ``.tinylogan`` config file
placed in your user's home. Read help above for details.

Results
=======

Let explain the given results::

    Starting from 15/Apr/2011:08:19:06
    enough... stopped by user action
    Ending at 28/Apr/2011:17:00:36
    Elapsed time: 0:00:04.955008
    Timedelta is 13 days, 8:41:30 (but only 7 days, 9:41:30 are counted due to time bounds)
    
    Top total time
      0001 - /url1 46591.603 (4924 times, average 9.462, 7.28% of the total)
      0002 - /url2 12660.053 (1212 times, average 10.446, 1.98% of the total)
      ...
    
    Top average time
      0001 - /url3 32.828 (15 times, 492 total)
      0002 - /url4 30.549 (7 times, 213 total)
      ...

``Starting from ...``
    First valid entry found in the log
``enough... stopped by user action``
    Only if you CTRL+C during the log analysis. This will stop the log scan and skip to results immediatly
``Ending at ...``
    Last entry analyzed
``Elapsed time: ...``
    Time required for the log analysis
``Timedelta is ...``
    Number of days from the first and last entry of the log, important for giving to the users a percent
    of the total time taken from an entry.
    
    If you use some of the time filters above the used value for the statistic is the one given in the
    sentence ``but only xxx are counted due to time bounds``.

Top total time
--------------

This will show, from the most consuming time to the less ones, a hierarchy of the URLs that take the most
time from the analyzed log::

    
            Total number of seconds taken
                         |                    Average time per call
    Entry position       |                             |
          |              |                             |
         0001 - /url1 46591.603 (4924 times, average 9.462, 7.28% of the total)
                  |               |                          |
           URL of the entry       |                          |
                                  |             Percentage of the total time
                             Times called

Top average time
----------------

This will show, from the most slow entry to the less ones, a hierarchy of the URLs that seems slowest,
considering the average time per hit.

Note that you could like to use the ``--min-times`` option for have a better statiscal report for this.
Without giving this option, a on-time call to a very slow procedure will probably be reported in this
hierarchy, even if it will not give you a good average data.

Let's details::

         Average number of seconds taken
                        |
    Entry position      |         Total time in seconds
          |             |                  |
         0001 - /url3 32.828 (15 times, 492 total)
                  |              |
           URL of the entry      |
                                 |
                            Times called

TODO
====

* a way to ignore min and max values from multiple occurrences of a match
* right now all records are stored in memory... obviously this is not the way to
  parse a potentially multiple-gigabyte-long-file
* a way to recognize default views (like: that ``foo/other_foo`` is the same as
  ``foo/other_foo/index.html``)
* right now the log is read from the first line. In this way reaching a far-from-first
  entry, when using the ``--start-date`` is used, can be *really* slow
