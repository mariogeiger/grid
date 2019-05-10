# pylint: disable=C
import argparse
import glob

import torch


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir1", type=str)
    parser.add_argument("log_dir2", type=str)
    args = parser.parse_args()

    runs = [
        [
            {
                key: value
                for key, value in r.__dict__.items()
                if key != 'pickle'
            }
            for r in [torch.load(path) for path in glob.glob("{}/*.pkl".format(log_dir))]
        ]
        for log_dir in [args.log_dir1, args.log_dir2]
    ]

    for key in {key for rs in runs for r in rs for key in r.keys()}:

        values = [
            {r[key] if key in r else None for r in rs}
            for rs in runs
        ]

        if values[0] != values[1]:
            try:
                values = [sorted(x) for x in values]
            except TypeError:
                pass
            print("{}: {}".format(key, values))


if __name__ == '__main__':
    main()
