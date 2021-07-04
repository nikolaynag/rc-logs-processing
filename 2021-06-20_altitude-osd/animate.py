#!/usr/bin/env python3
import argparse
import csv
from collections import OrderedDict
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        help="Input CSV file",
    )
    parser.add_argument(
        "--fps", type=int, default=25,
        help="Frames per second"
    )
    parser.add_argument(
        "--example-frame", type=float,
        help="Just show example frame for given time",
    )
    parser.add_argument(
        "--out-duration", type=float,
        help="Output duration in seconds",
    )
    parser.add_argument(
        "--dpi", type=float,
        default=192.0,
    )
    parser.add_argument(
        "field_name",
    )
    parser.add_argument(
        "start", type=float,
        help="Start time in seconds",
    )
    parser.add_argument(
        "duration", type=float,
        help="Data duration in seconds",
    )
    args = parser.parse_args()
    x = np.array([])
    y = np.array([])
    start_ts = None
    prev_val = None
    for row in read_objects_from_csv(args.input_file):
        ts_format = "%Y-%m-%d %H:%M:%S.%f"
        ts_str = "{Date} {Time}000".format(**row)
        timestamp = datetime.strptime(ts_str, ts_format).timestamp()
        if start_ts is None:
            start_ts = timestamp
        moment = timestamp - start_ts
        if moment < args.start or moment - args.start > args.duration:
            continue
        new_val = float(row[args.field_name])
        if new_val == prev_val:
            continue
        prev_val = new_val
        x = np.append(x, timestamp-start_ts)
        y = np.append(y, new_val)

    x = x - (x-1201.4)*1.0/113.  # time correction
    y = y - 6.1 - (6.5-6.1)*(x-1192)/(1317-1192)  # height correction
    fig = plt.figure(figsize=(10, 2), frameon=False)
    fig.patch.set_alpha(0.0)
    plt.gca().set_axis_off()
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.margins(0.2)
    plt.tight_layout()
    line, = plt.plot(x, y, "-r", linewidth=2)
    plt.xlim(min(x), max(x))
    point, = plt.plot(x[0], y[0], "or")
    text = plt.annotate(
        "{} m".format(y[0]),
        (x[0], y[0]),
        ma="center",
        xytext=(10, 0),
        textcoords="offset points",
        fontsize=25,
        color="r",
    )

    def init():
        return animate(0)

    def animate(i):
        seconds = args.start + i*1.0/args.fps
        ix = np.searchsorted(x, seconds)
        if ix > len(x) - 2:
            ix = len(x) - 2
        elif ix < 1:
            ix = 1
        interp_y = np.interp(seconds, x[ix-1:ix+1], y[ix-1:ix+1])
        px = np.append(x[:ix], seconds)
        py = np.append(y[:ix], interp_y)
        line.set_data(px, py)
        point.set_data(px[-1], py[-1])
        text.xy = (px[-1], py[-1])
        text.set_text("{:.1f} m".format(py[-1]))
        return line, point, text

    if args.example_frame is not None:
        animate(int(args.fps*args.example_frame))
        plt.show()
        return

    if args.out_duration is None:
        args.out_duration = args.duration
    ani = animation.FuncAnimation(
        fig, animate, init_func=init,
        interval=2, blit=True, save_count=int(args.out_duration*args.fps),
    )
    ani.save(
        'movie.mov', codec="png", fps=args.fps,
        dpi=args.dpi, bitrate=-1,
        savefig_kwargs={'transparent': True, 'facecolor': 'none'},
    )


if __name__ == "__main__":
    main()
