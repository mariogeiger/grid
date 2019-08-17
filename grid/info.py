# pylint: disable=C
import argparse
import glob
import os

import torch


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    args = parser.parse_args()

    if os.path.isfile("{}/info".format(args.log_dir)):
        with open("{}/info".format(args.log_dir), 'rb') as f:
            while True:
                try:
                    info = torch.load(f)
                except EOFError:
                    break
            print("last command")
            print(info['args'].cmd)
            print("git commit    {}".format(info['git']['log']))
            print("git status    {}".format(info['git']['status']))


    runs = [
        {
            key: value
            for key, value in r.__dict__.items()
            if key != 'pickle'
        }
        for r in [torch.load(path) for path in glob.glob("{}/*.pkl".format(args.log_dir))]
    ]

    for key in sorted({key for r in runs for key in r.keys()}):

        values = {r[key] if key in r else None for r in runs}

        try:
            values = sorted(values)
            values = " ".join([repr(x) for x in values])
        except TypeError:
            pass

        print("{}: {}".format(key, values))

    print("{} records in total (some can be empty!)".format(len(runs)))


if __name__ == '__main__':
    main()
