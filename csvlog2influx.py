#!/usr/bin/env python3
import argparse
import requests
import traceback
import csv
import sys
from collections import OrderedDict
from datetime import datetime

if sys.version_info < (3, 0):
    sys.stderr.write(
        "Sorry, this script could not run with Python {}.{}, "
        "Python 3.x is required\n".format(*sys.version_info))
    sys.exit(1)


def read_objects_from_csv(filename):
    with open(filename, "r", encoding="utf8") as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        headers = dict(
            (i, title) for i, title in enumerate(next(reader))
        )
        for line in reader:
            yield OrderedDict(
                (headers.get(i, "column_{}".format(i)), val)
                for i, val in enumerate(line)
            )


def send_points(args, points):
    def dict_to_keyvalue_str(d):
        return ",".join(["{}={}".format(k, d[k]) for k in d])
    lines = []
    for pnt in points:
        pnt["tags"] = dict_to_keyvalue_str(pnt["tags"])
        pnt["fields"] = dict_to_keyvalue_str(pnt["fields"])
        lines.append("{measurement},{tags} {fields} {timestamp}".format(**pnt))
    try:
        url = "{}/write?db={}&precision=ms".format(
            args.influx_url, args.db_name
        )
        if not args.dry_run:
            requests.post(url, data="\n".join(lines))
        else:
            sys.stdout.write("POST {}\n{}\n".format(url, "\n".join(lines)))
    except:
        traceback.print_exc()


def influx_escape(s):
    s = s.replace(",", "\\,")
    s = s.replace("=", "\\=")
    s = s.replace(" ", "\\ ")
    s = s.replace("(", "_")
    s = s.replace(")", "")
    return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db-name",
        help="Influxdb database name (default '%(default)s')",
        type=str,
        default="csvlogs",
    )
    parser.add_argument(
        "--model",
        help="Model name",
        type=str,
        default="unknown",
    )
    parser.add_argument(
        "--dry-run",
        help="Do not write anything, just print what would be done",
        action="store_true",
    )
    parser.add_argument(
        "--batch-cnt",
        help="Number of points to send to influx "
             "in one batch (default %(default)s)",
        default=100,
        type=int,
    )
    parser.add_argument(
        "--influx-url",
        help="URL to post data to influxdb in form http://IP:port "
             "(default %(default)s)",
        default="http://127.0.0.1:8086",
        type=str,
    )
    parser.add_argument(
        "input_file",
        help="Input CSV file",
    )
    args = parser.parse_args()

    points = []
    for row in read_objects_from_csv(args.input_file):
        tsFormat = "%Y-%m-%d %H:%M:%S.%f"
        tsStr = "{Date} {Time}000".format(**row)
        timestamp = datetime.strptime(tsStr, tsFormat).timestamp()
        fields = {
            influx_escape(k): float(v)
            for k, v in row.items()
            if k not in ["Date", "Time", "LSW"]
        }
        points.append(dict(
                measurement="csvlogs",
                timestamp=int(timestamp*1000),
                tags=dict(model=influx_escape(args.model)),
                fields=fields
        ))
        if len(points) >= args.batch_cnt:
            send_points(args, points)
            sys.stderr.write("Uploaded {} points\n".format(len(points)))
            points.clear()
    send_points(args, points)
    sys.stderr.write("Uploaded {} points\n".format(len(points)))

if __name__ == "__main__":
    main()
