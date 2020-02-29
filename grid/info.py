# pylint: disable=eval-used, missing-docstring, invalid-name, line-too-long
import argparse
import glob
import os

import torch

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    def tqdm(x):
        return x


def print_info(argss, thr=5):
    def hashable(x):
        if isinstance(x, list):
            x = tuple(x)
        if isinstance(x, set):
            x = frozenset(x)
        try:
            hash(x)
        except TypeError:
            return '<not hashable>'
        return x

    argss = [
        {
            key: hashable(value)
            for key, value in r.__dict__.items()
            if key != 'pickle'
        }
        for r in argss
    ]

    def keyf(key):
        return (len({r[key] if key in r else None for r in argss}), key)

    for key in sorted({key for r in argss for key in r.keys()}, key=keyf):

        values = {r[key] if key in r else None for r in argss}
        values = [(x, len([1 for r in argss if (x is None and key not in r) or (key in r and r[key] == x)])) for x in values]
        n = len(values)

        try:
            values = sorted(values)
        except TypeError:
            pass

        if n == 1:
            text = " ".join(["{}".format(repr(x)) for x, m in values])
            print("{}: {}".format(key, text))
        elif n <= thr:
            text = " ".join(["{}({} runs)".format(repr(x), m) for x, m in values])
            print("{}: {}".format(key, text))
        else:
            text = " ".join([repr(x) for x, m in values])
            print("{}: ({} values) {}".format(key, n, text))

    print("{} records in total (some can be empty!)".format(len(argss)))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    parser.add_argument("--thr", type=int, default=5)
    parser.add_argument("--pred", type=str)
    args = parser.parse_args()

    pred_args = eval(args.pred) if args.pred else None

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

    argss = (torch.load(path) for path in tqdm(glob.glob("{}/*.pkl".format(args.log_dir))))
    argss = (a for a in argss if pred_args is None or pred_args(a))

    print_info(argss, args.thr)


if __name__ == '__main__':
    main()
