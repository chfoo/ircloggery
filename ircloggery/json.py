import datetime
import json


def read_json_multiline(file):
    '''Read JSON text that is indented onto multiple lines.

    The input must look like this::

        {
            "key": value,
            "key": value,
            "key": value
        }
    '''

    while True:
        line = file.readline().strip()

        if not line:
            break

        if line == '{':
            lines = [line]
        elif line == '}':
            lines.append(line)

            doc = json.loads(''.join(lines))

            doc['date'] = datetime.datetime.strptime(doc['date'], '%Y-%m-%dT%H:%M:%S+00:00').replace(tzinfo=datetime.timezone.utc)

            yield doc
        else:
            lines.append(line)
