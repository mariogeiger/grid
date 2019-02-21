# pylint: disable=C
import argparse
import glob

import torch


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    args = parser.parse_args()


    runs = [
        {
            key: value
            for key, value in r.__dict__.items()
            if key != 'pickle'
        }
        for r in [torch.load(path) for path in glob.glob("{}/*.pkl".format(args.log_dir))]
    ]

    for key in {key for r in runs for key in r.keys()}:

        values = {r[key] if key in r else None for r in runs}

        print("{}: {}".format(key, values))


if __name__ == '__main__':
    main()
