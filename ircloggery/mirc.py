import datetime
import re

import arrow


def read_mirc(file, filename, time_zone='UTC'):
    match = re.search(r'_(\d{4})(\d{2})(\d{2})\.log', filename)

    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))

    for line in file:
        line = line.lstrip().rstrip('\r\n')

        if not line:
            continue

        match = re.match(r'\[(\d{2}):(\d{2}):(\d{2})\] (\S+) (.+)', line)

        hour = int(match.group(1))
        minute = int(match.group(2))
        sec = int(match.group(3))

        date = arrow.get(datetime.datetime(year, month, day, hour, minute, sec),
                         time_zone)

        source = match.group(4)
        text = match.group(5)

        if source == '***':
            yield {
                'type': 'event',
                'text': text,
                'date': date
            }
        elif source == '*':
            source, text = text.split(' ', 1)
            yield {
                'type': 'action',
                'text': text,
                'date': date,
                'nick': source,
            }
        else:
            if source[0] in '<-' and source[-1] in '>-':
                source = source[1:-1]

            yield {
                'type': 'message',
                'text': text,
                'nick': source,
                'date': date
            }
