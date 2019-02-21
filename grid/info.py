# pylint: disable=
import argparse
import glob
import os

import torch


def tup(args):
    d = [(key, value) for key, value in args.__dict__.items() if key != 'pickle']
    return tuple(sorted(d))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    args = parser.parse_args()


    runs = [torch.load(path) for path in glob.glob("{}/*.pkl".format(args.log_dir))]
    runs = [
        {
            key: value
            for key, value in r.__dict__.items()
            if key != 'pickle'
        }
        for r in runs
    ]

    keys = {key for r in runs for key in r.keys()}

    union = {
        key: {r[key] if key in r else None for r in runs}
        for key in keys
    }

    for key, values in union.items():
        print("{}: {}".format(key, values))


if __name__ == '__main__':
    main()
