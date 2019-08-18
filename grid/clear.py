# pylint: disable=C
import argparse
import glob
import os

import torch

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    tqdm = lambda x: x


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    args = parser.parse_args()

    def tup(args):
        d = [(key, value) for key, value in args.__dict__.items() if key != 'pickle']
        return tuple(sorted(d))

    done = set()

    for path in tqdm(sorted(glob.glob("{}/*.pkl".format(args.log_dir)))):
        with open(path, 'rb') as f:
            args = tup(torch.load(f))
            try:
                torch.load(f, map_location='cpu')
            except EOFError:
                print("rm empty: {}".format(path))
                os.remove(path)
                continue

            if args in done:
                print("rm clone: {}".format(path))
                os.remove(path)
                continue

            done.add(args)


if __name__ == '__main__':
    main()
