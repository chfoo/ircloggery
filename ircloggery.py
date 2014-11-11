'''Combine and convert xchat2/bip logs into mirc irclogger logs.'''
# Copyright 2014 Christopher Foo
# License: GPLv3
import argparse
import calendar
import datetime
import os
import re


MONTH_STR_MAP = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12,
}

DAY_OF_WEEK_MAP = {
    0: 'Mon',
    1: 'Tue',
    2: 'Wed',
    3: 'Thu',
    4: 'Fri',
    5: 'Sat',
    6: 'Sun',
}


def read_xchat2(file):
    prev_month = None

    for line in file:
        line = line.rstrip()

        if not line:
            continue

        if line.startswith('**** '):
            match = re.search(r'(\w{3})  ?(\d{1,2}) (\d{2}):(\d{2}):(\d{2}) (\d{4})', line)

            year = int(match.group(6))
            month = MONTH_STR_MAP[match.group(1)]
            day = int(match.group(2))
            hour = int(match.group(3))
            minute = int(match.group(4))
            sec = int(match.group(5))

            yield {
                'type': 'event',
                'text': line[5:],
                'date': datetime.datetime(year, month, day, hour, minute, sec,
                                          tzinfo=datetime.timezone.utc)
            }
            continue

        match = re.match(r'(\w{3}) (\d{2}) (\d{2}):(\d{2}):(\d{2}) (\S+)\t(.*)', line)

        if not match:
            print(repr(line))
            continue

        month = MONTH_STR_MAP[match.group(1)]
        day = int(match.group(2))
        hour = int(match.group(3))
        minute = int(match.group(4))
        sec = int(match.group(5))

        if prev_month and prev_month == 12 and month == 1:
            year += 1

        prev_month = month

        date = datetime.datetime(year, month, day, hour, minute, sec,
                                 tzinfo=datetime.timezone.utc)

        source = match.group(6)
        text = match.group(7)

        if source == '*':
            # FIXME: this might be a /me
            yield {
                'type': 'event',
                'text': text,
                'date': date
            }
        else:
            yield {
                'type': 'message',
                'text': text,
                'nick': source.lstrip('<-').rstrip('>-'),
                'date': date
            }


def read_bif(file):
    for line in file:
        line = line.strip()

        if not line:
            continue

        match = re.match(r'(\d{2})-(\d{2})-(\d{4}) (\d{2}):(\d{2}):(\d{2}) ([<>!-]+) (\S+) (.*)', line)

        if not match:
            print(repr(line))
            continue

        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        sec = int(match.group(6))

        event_type = match.group(7)
        source = match.group(8)
        text = match.group(9)

        date = datetime.datetime(year, month, day, hour, minute, sec,
                                 tzinfo=datetime.timezone.utc)

        if event_type == '-!-':
            yield {
                'type': 'event',
                'text': '{} {}'.format(source, text),
                'date': date
            }
        else:
            if source == '*':
                source, dummy, text = text.partition(' ')
                yield {
                    'type': 'action',
                    'text': text,
                    'nick': source.partition('!')[0].rstrip(':'),
                    'date': date
                }
            else:
                yield {
                    'type': 'message',
                    'text': text,
                    'nick': source.partition('!')[0].rstrip(':'),
                    'date': date
                }


def write_record(file_cache, dest_dir, record, censor_hostnames=False):
    year = record['date'].year
    month = record['date'].month
    day = record['date'].day
    year = record['date'].year
    day_of_week = DAY_OF_WEEK_MAP[calendar.weekday(year, month, day)]

    filename = '{:04}-{:02}-{:02},{}.log'.format(year, month, day, day_of_week)

    path = os.path.join(dest_dir, filename)

    if path not in file_cache:
        file = file_cache[path] = open(path, 'w')
    else:
        file = file_cache[path]

    hour = record['date'].hour
    minute = record['date'].minute

    if record['type'] == 'event':
        source = '***'
    elif record['type'] == 'action':
        source = '* {}'.format(record['nick'])
    else:
        source = '<{}>'.format(record['nick'])

    text = record['text']

    if censor_hostnames and record['type'] == 'event' and \
            not re.search(r' ban |mode/', text):
        text = re.sub(r'@([a-zA-Z0-9.:_-]+)', '@[redacted]', text)

    line = '[{:02}:{:02}] {} {}\n'.format(hour, minute, source, text)

    file.write(line)


def sniff_type(file):
    line = file.readline()
    file.seek(0)

    if line.startswith('****'):
        return 'xchat2'
    else:
        return 'bif'


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('source_file', nargs='+',
                            type=argparse.FileType('r', encoding='utf-8',
                                                   errors='replace'))
    arg_parser.add_argument('dest_dir')
    arg_parser.add_argument('--censor-hostnames', action='store_true')

    args = arg_parser.parse_args()

    # TODO: don't store in memory
    records = {}

    for file in args.source_file:
        if sniff_type(file) == 'xchat2':
            read_func = read_xchat2
        else:
            read_func = read_bif

        for record in read_func(file):
            records[(record['date'], record['text'])] = record

    prev_record = None
    file_cache = {}

    for record_date, text in sorted(records):
        record = records[(record_date, text)]

        if prev_record and \
                abs((prev_record['date'] - record['date']).total_seconds()) < 5 and \
                prev_record['text'] == text:
            # duplicate
            pass
        else:
            write_record(file_cache, args.dest_dir, record,
                         censor_hostnames=args.censor_hostnames)

        prev_record = record


if __name__ == '__main__':
    main()
