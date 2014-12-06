import argparse
import functools

import ircloggery.bif
import ircloggery.writer
import ircloggery.xchat
import ircloggery.json
import ircloggery.mirc


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('source_file', nargs='+')
    arg_parser.add_argument('dest_dir')
    arg_parser.add_argument('--censor-hostnames', action='store_true')
    arg_parser.add_argument('--remove-duplicates', action='store_true')
    arg_parser.add_argument('--timezone', default='UTC')

    args = arg_parser.parse_args()

    # TODO: don't store in memory
    records = {}

    for filename in args.source_file:
        file = open(filename, 'r', encoding='utf-8', errors='replace')

        file_type = ircloggery.writer.sniff_type(file)
        if file_type == 'xchat2':
            read_func = functools.partial(
                ircloggery.xchat.read_xchat2, time_zone=args.timezone
            )
        elif file_type == 'json':
            read_func = ircloggery.json.read_json_multiline
        elif file_type == 'mirc':
            read_func = functools.partial(
                ircloggery.mirc.read_mirc, filename=filename,
                time_zone=args.timezone
            )
        else:
            read_func = ircloggery.bif.read_bif

        for record in read_func(file):
            records[(record['date'], record['text'])] = record

    prev_record = None
    file_cache = {}

    for record_date, text in sorted(records):
        record = records[(record_date, text)]

        if args.remove_duplicates and prev_record and \
                        abs((prev_record['date'] - record['date']).total_seconds()) < 5 and \
                        prev_record['text'] == text:
            # duplicate
            pass
        else:
            ircloggery.writer.write_record(file_cache, args.dest_dir, record,
                         censor_hostnames=args.censor_hostnames)

        if len(file_cache) > 100:
            file_cache.popitem()[1].close()

        prev_record = record


if __name__ == '__main__':
    main()
