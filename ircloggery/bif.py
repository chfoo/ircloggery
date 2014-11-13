import datetime
import re


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
