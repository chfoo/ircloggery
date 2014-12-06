import datetime
import re

import arrow

from ircloggery.strings import MONTH_STR_MAP


def read_xchat2(file, time_zone='UTC'):
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
                'date': arrow.get(datetime.datetime(year, month, day,
                                                    hour, minute, sec),
                                  time_zone
                                  )
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
