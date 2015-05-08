import datetime
import re
import sys

import arrow


def read_textual(file):
    for line in file:
        line = line.rstrip()

        if not line:
            continue

        match = re.match(r'\[(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})([\d+-]+)\] (.*)', line)

        if not match:
            print('textual: unknown line ', repr(line), file=sys.stderr)
            continue

        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        hour = int(match.group(4))
        minute = int(match.group(5))
        sec = int(match.group(6))
        time_zone = match.group(7)
        rest = match.group(8)

        date = arrow.get(datetime.datetime(year, month, day,
                                           hour, minute, sec),
                         time_zone
                         )

        if rest.startswith('<'):
            match = re.match(r'<([^>]+)> (.*)', rest)

            nick = match.group(1)
            nick = nick.lstrip('@+')

            text = match.group(2)

            yield {
                'type': 'message',
                'text': text,
                'nick': nick,
                'date': date
            }
        else:
            # FIXME: could be a /me
            yield {
                'type': 'event',
                'text': rest,
                'date': date
            }
