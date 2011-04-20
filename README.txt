.. contents:: **Table of contents**

Tiny Log Analizer
=================

This utility only works with Apache-like access HTTP log where the response time data is enabled.

To know how to do this, see `this blog post`__ or, in brief change the configuration of your log format
from something like::

    LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined

To this::

    LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %T/%D" combined

The log record will change to something like this::

    [31/Jan/2008:14:19:07 +0000] "GET / HTTP/1.1" 200 7918 "" "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.11) Gecko/20061201 Firefox/2.0.0.11 (Ubuntu-feisty)" 0/95491

__ http://www.ducea.com/2008/02/06/apache-logs-how-long-does-it-take-to-serve-a-request/ 

Seconds and microsends
----------------------

The tool only care about microsends (`%D`) so you need to have Apache 2.


