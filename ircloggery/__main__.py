import argparse

import ircloggery.bif
import ircloggery.writer
import ircloggery.xchat


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
        if ircloggery.writer.sniff_type(file) == 'xchat2':
            read_func = ircloggery.xchat.read_xchat2
        else:
            read_func = ircloggery.bif.read_bif

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
            ircloggery.writer.write_record(file_cache, args.dest_dir, record,
                         censor_hostnames=args.censor_hostnames)

        prev_record = record


if __name__ == '__main__':
    main()
