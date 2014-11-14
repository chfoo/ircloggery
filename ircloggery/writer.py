import calendar
import os
import re

from ircloggery.strings import DAY_OF_WEEK_MAP


def write_record(file_cache, dest_dir, record, censor_hostnames=False):
    year = record['date'].year
    month = record['date'].month
    day = record['date'].day
    year = record['date'].year
    day_of_week = DAY_OF_WEEK_MAP[calendar.weekday(year, month, day)]

    filename = '{:04}-{:02}-{:02},{}.log'.format(year, month, day, day_of_week)

    path = os.path.join(dest_dir, filename)

    if path not in file_cache:
        file = file_cache[path] = open(path, 'a')
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
    elif line.startswith('{'):
        return 'json'
    else:
        return 'bif'
