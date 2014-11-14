import argparse
import datetime
import json
import os
import re
import time

import requests
from ircloggery.strings import MONTH_STR_MAP


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('channel')
    arg_parser.add_argument('date')
    arg_parser.add_argument('dest_dir')

    args = arg_parser.parse_args()

    year, month, day = re.match(r'(\d{4})-(\d{2})-(\d{2})', args.date).groups()

    date = datetime.date(int(year), int(month), int(day))

    num_misses = 0

    while True:
        if num_misses > 60:
            break

        print(date, end=' ')

        path = os.path.join(args.dest_dir, '{}.txt'.format(date.isoformat()))

        if os.path.exists(path):
            date = date - datetime.timedelta(1)

            if isinstance(date, datetime.datetime):
                date = date.date()

            continue

        response = requests.get(
            'http://badcheese.com/~steve/atlogs/',
            params={'chan': args.channel, 'day': date.isoformat()}
        )

        print(response.url)

        response.raise_for_status()

        matches = tuple(re.finditer(r'<tr><td valign=top>([^<]+)</td><td valign=top><font color=#AA0000>(.+)</font></td><td valign=top>(.*)</td></tr>', response.text))

        if not matches:
            num_misses += 1
        else:
            num_misses = 0

        with open(path, 'w') as file:
            for match in matches:
                date = match.group(1)
                source = match.group(2)
                text = match.group(3)

                date_match = re.match('(\w{3})_(\d{2})_(\d{4})_(\d{2}):(\d{2}):(\d{2})', date)

                month = MONTH_STR_MAP[date_match.group(1)]
                day = int(date_match.group(2))
                year = int(date_match.group(3))
                hour = int(date_match.group(4))
                minute = int(date_match.group(5))
                second = int(date_match.group(6))

                date = datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)

                record = {
                    'date': date.isoformat(),
                    'text': text,
                }

                if source.startswith('* '):
                    record['type'] = 'action'
                    record['nick'] = source[2:]
                else:
                    record['type'] = 'message'
                    record['nick'] = source

                json.dump(record, file, indent=2)
                file.write('\n')

        date = date - datetime.timedelta(1)

        if isinstance(date, datetime.datetime):
            date = date.date()

        time.sleep(0.25)

if __name__ == '__main__':
    main()
