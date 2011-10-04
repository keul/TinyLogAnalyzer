#! /usr/bin/python
# -*- coding: utf-8 -*-

# "172.16.245.69 - - [11/Apr/2011:16:06:10 +0200] GET /URL HTTP/1.1" 200 55 7/7124818
# "172.16.245.69 - - [11/Apr/2011:16:06:10 +0200] GET /URL HTTP/1.1" 304 - 0/15625

import sys
import re
import optparse
import logging
import os.path

import ConfigParser

from datetime import datetime, date, time, timedelta

# greedy
#PATTERN = r"""[^[]*\[(?P<date>\d\d/\w*/\d{4})\:(?P<time>\d\d\:\d\d\:\d\d)[^[]*\] "(?:GET|POST) (?P<url>[^?]*)(?P<querystring>\?.*)? HTTP/.*" (?P<code>\d\d\d).*(?P<sec>\d+)/(?P<micros>\d+)"""
# non-greedy
PATTERN = r""".*?\[(?P<date>.*?)\:(?P<time>\d\d\:\d\d\:\d\d).*?\] "(?:GET|POST) (?P<url>.*?)(?P<querystring>\?.*?)? HTTP\/.*?" (?P<code>\d\d\d).*(?P<sec>\d+)\/(?P<micros>\d+)"""
logLine = re.compile(PATTERN, re.I)

DAY_PATTERN = r"""^(?P<day>today|yesterday|tomorrow|week|month|year)(?:(?P<modifier>\+|\-)(?P<qty>\d+))?$"""
dateControl = re.compile(DAY_PATTERN, re.I)

version = "0.4.0"
description = "Simple bash utility for analyze HTTP access log with enabled response time"

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

logger = logging.getLogger('TinyLogAnalyzer')
logging.basicConfig(level=logging.INFO)

HOME = os.path.expanduser('~')


def numeric_compare_total(x, y):
    return x['micros'] - y['micros']


def numeric_compare_average(x, y):
    return x['average'] - y['average']


def str2date(st):
    dd, mmm, yyyy = st.split('/')
    return date(int(yyyy), MONTHS.index(mmm) + 1, int(dd))


def str2datetime(st):
    """string date in format dd/Mon/aaaa:hh:mm:ss
    11/Apr/2011:16:06:10
    """
    dd, mmm, yyyy, hh, mm, ss = st[:2], st[3:6], st[7:11], st[12:14], st[15:17], st[18:20]
    return datetime(int(yyyy), MONTHS.index(mmm) + 1, int(dd), int(hh), int(mm), int(ss))


def parseDate(st):
    m = dateControl.match(st)
    if m:
        base = m.groupdict()['day']
        modifier = m.groupdict()['modifier']
        qty = m.groupdict()['qty']
        if base == 'today':
            resDate = date.today()
        elif base == 'yesterday':
            resDate = date.today() - timedelta(days=1)
        elif base == 'tomorrow':
            resDate = date.today() + timedelta(days=1)
        elif base == 'week':
            resDate = date.today()
            resDate -= timedelta(resDate.weekday())
        elif base == 'month':
            resDate = date.today()
            resDate -= timedelta(resDate.day - 1)
        # now modifiers (optional)
        if modifier and qty:
            qty = int(qty)
            if modifier == '+':
                resDate += timedelta(qty)
            else:
                resDate -= timedelta(qty)
        return resDate
    # dd/Mmm/aaaa
    return str2date(st)


def parseTime(st):
    try:
        hh, mm, ss = st.split(':')
    except ValueError:
        hh, mm = st.split(':')
        ss = 0
    return time(int(hh), int(mm), int(ss))


def reduceTime(seconds, td_diff, skip_time_start, skip_time_end, days_skipped):
    if td_diff.days > 0:
        if skip_time_start:
            t1 = parseTime(skip_time_start)
            amount1 = t1.hour * 3600
            amount1 += t1.minute * 60
            amount1 += t1.second
            seconds -= amount1 * td_diff.days
        if skip_time_end:
            t2 = parseTime(skip_time_end)
            amount2 = (24 - t2.hour) * 3600
            # let's REMOVE minutes and seconds
            amount2 -= t2.minute * 60
            amount2 -= t2.second
            seconds -= amount2 * td_diff.days
        if days_skipped:
            seconds -= (24 * 3600) * days_skipped
            # I already reduced the total for filter like skip_time_start and
            # skip_time_end, so... now I need to re-add them
            if skip_time_start:
                seconds += amount1 * days_skipped
            if skip_time_end:
                seconds += amount2 * days_skipped
    return seconds


def analyze(options, logfile):
    log = open(logfile)

    if options.verbose:
        logger.setLevel(logging.DEBUG)

    registry = {}
    topTotal = []
    topAverage = []
    lastProcessedDate = None
    lastProcessedTime = None
    days_skipped = 0

    first = True
    parsingStart = datetime.now()
    cnt = 0
    try:
        for l in log:
            cnt += 1
            matches = logLine.match(l)
            if matches is None:
                logger.warn("Line %d doesn't match the required format\n%s" % (cnt, l))
                continue

            lineData = matches.groupdict()
            ref_date = str2date(lineData['date'])

            # {'url': '/URL', 'sec': '7', 'code': '200', 'micros': '7124818'}
            url = lineData['url']
            if url.endswith('/') and url != '/':
                url = url[:-1]

            curMicros = int(lineData['micros'])
            # min time check
            if options.min_time and curMicros < options.min_time * 1000:
                continue
            # max time check
            if options.max_time and curMicros > options.max_time * 1000:
                continue

            # choosed to keep querystrings
            if options.keep_query:
                querystring = lineData['querystring']
                if querystring:
                    url += querystring

            # start date filters
            if options.start_date:
                start_date = parseDate(options.start_date)
                if ref_date < start_date:
                    continue

            # end date filters
            if options.end_date:
                end_date = parseDate(options.end_date)
                if ref_date > end_date:
                    break

            # include only...
            stop = False
            if options.includes:
                stop = True
                for i in options.includes:
                    if re.search(i, url, re.IGNORECASE) is not None:
                        stop = False
                        break
            if stop:
                continue

            # exclude all
            stop = False
            for e in options.excludes:
                if re.search(e, url, re.IGNORECASE) is not None:
                    stop = True
                    break
            if stop:
                continue

            # day filter: other times in the same day
            stop = False
            for dreg in options.skip_days:
                if re.search(dreg, lineData.get('date')) is not None:
                    stop = True
                    if lastProcessedDate and lineData.get('date') != lastProcessedDate:
                        logger.debug("Skipping %s due to filters" % lineData.get('date'))
                        days_skipped += 1

            if lastProcessedDate and lineData.get('date') != lastProcessedDate and not stop:
                logger.debug("...now analyzing %s" % lineData.get('date'))

            lastProcessedDate = lineData.get('date')
            lastProcessedTime = lineData.get('time')

            if stop:
                continue

            # not before time
            if options.skip_time_start:
                refTime = parseTime(options.skip_time_start)
                lastTime = parseTime(lastProcessedTime)
                if lastTime < refTime:
                    continue

            # not after time
            if options.skip_time_end:
                refTime = parseTime(options.skip_time_end)
                lastTime = parseTime(lastProcessedTime)
                if lastTime > refTime:
                    continue

            if first:
                print "Starting from %s:%s" % (lastProcessedDate, lastProcessedTime)
                firstDateTime = str2datetime("%s:%s" % (lastProcessedDate, lastProcessedTime))
                first = False

            if not registry.get(url):
                registry[url] = {'micros': curMicros, 'times': 1, 'url': url}
            else:
                registry[url]['micros'] = registry[url]['micros'] + curMicros
                registry[url]['times'] += 1

            # data for statistics
            registry[url]['average'] = registry[url]['micros'] / registry[url]['times']

    except KeyboardInterrupt:
        # first CTRL+C don't stop the program
        print "\nEnough... stopped by user action"
    except:
        logger.exception("Error parsing log at line %d\n%s" % (cnt, l))
        raise

    # ******* now collect statistical data *******
    for m, record in registry.items():
            # Top total time
            try:
                topTotal.index(record)
            except ValueError:
                topTotal.append(record)
                topTotal.sort(numeric_compare_total, reverse=True)
                topTotal = topTotal[:options.size]

            # top average time
            if not options.min_times or options.min_times <= record['times']:
                try:
                    topAverage.index(record)
                except ValueError:
                    topAverage.append(record)
                    topAverage.sort(numeric_compare_average, reverse=True)
                    topAverage = topAverage[:options.size]

    log.close()
    requiredTime = datetime.now() - parsingStart

    if first:
        # no row parsed at all
        print "No row parsed in the given range"
        sys.exit(0)

    lastDateTime = str2datetime("%s:%s" % (lastProcessedDate, lastProcessedTime))

    print "Ending at %s:%s" % (lastProcessedDate, lastProcessedTime)
    print "Elapsed time: %s" % requiredTime
    td_diff = lastDateTime - firstDateTime
    diff_seconds = (td_diff.microseconds + (td_diff.seconds + td_diff.days * 24 * 3600) * 10 ** 6) / 10 ** 6

    # if I use skip-timeperiod_start/end I need to remove values from this list
    if options.skip_time_start or options.skip_time_end or options.skip_days:
        diff_seconds = reduceTime(diff_seconds, td_diff, options.skip_time_start, options.skip_time_end, days_skipped)
        print "Timedelta is %s (but only %s are counted due to time bounds)" % (td_diff, timedelta(seconds=diff_seconds))
    else:
        print "Timedelta is %s (%s seconds)" % (td_diff, diff_seconds)
    print ""

    print "Top total time"
    cnt = 0
    for x in topTotal:
        cnt += 1
        print "  %04d - %s %0.3f (%d times, average %0.3f, %0.2f%% of the total)" % (
                           cnt,
                           x['url'],
                           float(x['micros']) / (10 ** 6),
                           x['times'],
                           float(x['micros']) / x['times'] / (10 ** 6),
                           (float(x['micros']) / (10 ** 6)) * 100 / float(diff_seconds),
                           )
    print ""
    print "Top average time"
    cnt = 0
    for x in topAverage:
        cnt += 1
        print "  %04d - %s %0.3f (%d times, %d total)" % (
                          cnt,
                          x['url'],
                          float(x['average']) / (10 ** 6),
                          x['times'],
                          float(x['average']) / (10 ** 6) * x['times'],
                          )


def main():
    args = sys.argv[1:]

    defaults = {'size': 50, 'keep-query': False, 'min-time': 0, 'max-time': 0, 'min-times': 0,
                'start-date': None, 'end-date': None, 'skip-time-start': None, 'skip-time-end': None,
                'skip-timeperiod-start': None, 'skip-timeperiod-end': None,
                'includes': [], 'excludes': [], 'skip-days': [],
                }

    # Load user default settings
    if '-U' not in args and os.path.exists(os.path.join(HOME, '.tinylogan')):
        cfile = open(os.path.join(HOME, '.tinylogan'), 'r')
        config = ConfigParser.SafeConfigParser()
        config.readfp(cfile)
        cfile.close()

        # I need to fake-read the argument -c now
        if '-c' in args:
            config_profile = args[args.index('-c') + 1]
            if not config.has_section(config_profile):
                print 'Section "%s" not found in %s' % (config_profile, os.path.join(HOME, '.tinylogan'))
                sys.exit(1)
        else:
            config_profile = 'DEFAULT'

        # numerical
        for param in ('size', 'min-time', 'max-time', 'min-times', ):
            if config.has_option(config_profile, param):
                defaults[param] = config.getint(config_profile, param)
        # boolean
        for param in ('keep-query', ):
            if config.has_option(config_profile, param):
                defaults[param] = config.getboolean(config_profile, param)
        # strings
        for param in ('start-date', 'end-date', 'skip-timeperiod-start', 'skip-timeperiod-end', ):
            if config.has_option(config_profile, param):
                defaults[param] = config.get(config_profile, param)
        # multis
        for param in ('includes', 'excludes', 'skip-days'):
            if config.has_option(config_profile, param):
                defaults[param] = [x.strip() for x in config.get(config_profile, param).splitlines() if x]

    usage = "usage: %prog [options] logfile"
    p = optparse.OptionParser(usage=usage, version="%prog " + version, description=description,
                              prog="tinylogan")
    p.remove_option("--help")
    p.add_option('--help', '-h', action="store_true", default=False, help='show this help message and exit')
    p.add_option('--verbose', '-v', action="count", default=0, help='verbose output during log analysis')
    p.add_option('--size', '-s', type="int", dest="size", default=defaults['size'],
                 help="choose the number of record to store in every log")
    p.add_option('--keep-query', '-q', dest="keep_query", default=defaults['keep-query'], action="store_true",
                 help="keep query strings in URLs instead of cutting them. "
                      "Using this an URL with different query string is treat like different URLs.")
    p.add_option('--include', '-i', dest="includes", default=defaults['includes'], action="append", metavar="INCLUDE_REGEX",
                 help="a regexp expression that an URLs must match of will be discarded. "
                      "Can be called multiple times, expanding the set")
    p.add_option('--exclude', '-e', dest="excludes", default=defaults['excludes'], action="append", metavar="EXCLUDE_REGEX",
                 help="a regexp expression that an URLs must not match of will be discarded. "
                      "Can be called multiple times, reducing the set")
    p.add_option('--skip-day', dest="skip_days", default=defaults['skip-days'], action="append", metavar="SKIP_DAY",
                 help="A regexp that repr specific whole day or a set of dates that must be ignored. Can be called multiple times")
    p.add_option('--min-time', type="int", dest="min_time", default=defaults['min-time'], metavar="MIN_TIME_MILLIS",
                 help="ignore all entries that require less than this amount of millisecs")
    p.add_option('--max-time', type="int", dest="max_time", default=defaults['max-time'], metavar="MAX_TIME_MILLIS",
                 help="ignore all entries that require more than this amount of millisecs")
    p.add_option('--min-times', type="int", dest="min_times", default=defaults['min-times'], metavar="MIN_TIMES",
                 help="set a minimum number of times that a entry must be found to be used in the \"Top average time\" statistic")

    group = optparse.OptionGroup(p, "Date filters",
                                    "For those kind of filters you need to specify a date.\n"
                                    "You are free to use a specific date in the format dd/mmm/aaaa, like "
                                    "\"24/May/2011\", but also some keywords for relative date like "
                                    "\"today\", \"yesterday\", \"tomorrow\", \"week\" and \"month\".\n"
                                    "Use of \"week\" and \"month\" mean referring to first day of the current "
                                    "week or month.\n"
                                    "You can also provide a numerical modifier using \"+\" or \"-\" followed by "
                                    "a day quantity\n"
                                    "(example: \"week-5\" for going back of 5 days from the start of the week)."
                                    )

    group.add_option('--start-date', dest="start_date", default=defaults['start-date'],
                 help="date where to start analyze and record")
    group.add_option('--end-date', dest="end_date", default=defaults['end-date'],
                 help="date where to end analyze and record")
    p.add_option_group(group)

    group = optparse.OptionGroup(p, "Time filters",
                                    "When a time is needed, you must enter it in the format hh:mm:ss or simply "
                                    "hh:mm, like \"09:21:30\" or \"09:21\".\n"
                                    "Those filter are used for skip record that are registered \"too late at night\" "
                                    "or \"too early in the morning\".")
    group.add_option('--skip-timeperiod-start', dest="skip_time_start", default=defaults['skip-timeperiod-start'],
                 help="do not analyse records before the given time")
    group.add_option('--skip-timeperiod-end', dest="skip_time_end", default=defaults['skip-timeperiod-end'],
                 help="do not analyse records later the given time")
    p.add_option_group(group)

    group = optparse.OptionGroup(p, "Default configuration profiles",
                                    "You can read a set of default configuration options from a \".tinylogan\" file "
                                    "placed in the user's home directory.\n"
                                    "If this file is found, parameters from the \"DEFAULT\" section are read, but you "
                                    "can also add other sections.\n"
                                    "You can always override those options from the command line."
                                    )
    # All foos below are ignored, we read them before the args parsing take place
    # We still need them for documentation and for evade argparse errors
    group.add_option('-c', dest="foo", default='default', metavar="PROFILE",
                 help="read a different profile section than DEFAULT")
    group.add_option('-U', dest="foo", default=False, action="store_true",
                 help="Ignore the user default profile file (if exists)")
    group.add_option('--example-profile', dest="example_profile", default=False, action="store_true",
                 help="Print out an example profile file, then exit. "
                      "You can put this output in a \".tinylogan\" file in your home, then customize it")

    p.add_option_group(group)

    options, arguments = p.parse_args(args)

    if options.example_profile:
        default_path = os.path.dirname(__file__)
        try:
            # distributed version
            f = open(os.path.join(default_path, 'profiles', 'example_profile.cfg'))
        except IOError:
            # will not fail only when calling the .py file directly
            f = open(os.path.join(default_path, 'example_profile.cfg'))
        print '\n'
        print f.read()
        f.close()
        sys.exit(0)

    if options.help or not arguments:
        p.print_help()
        sys.exit(0)

    try:
        analyze(options, arguments[0])
    except KeyboardInterrupt:
        print "Stopped by user action"
        sys.exit(1)

if __name__ == '__main__':
    main()
