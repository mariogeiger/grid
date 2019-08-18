# pylint: disable=C
import argparse
import glob
import os

import torch


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    parser.add_argument("--thr", type=int, default=5)
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
        values = [(x, len([1 for r in runs if (x is None and key not in r) or (key in r and r[key] == x)])) for x in values]
        n = len(values)

        try:
            values = sorted(values)
        except TypeError:
            pass

        if n == 1:
            text = " ".join(["{}".format(repr(x)) for x, m in values])
            print("{}: {}".format(key, text))
        elif n <= args.thr:
            text = " ".join(["{}({} runs)".format(repr(x), m) for x, m in values])
            print("{}: {}".format(key, text))
        else:
            text = " ".join([repr(x) for x, m in values])
            print("{}: ({} values) {}".format(key, n, text))

    print("{} records in total (some can be empty!)".format(len(runs)))


if __name__ == '__main__':
    main()
