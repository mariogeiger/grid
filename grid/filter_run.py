# pylint: disable=C, eval-used
import argparse
import glob
import os

import torch


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    parser.add_argument("filter", type=str)
    args = parser.parse_args()

    f = eval(args.filter)

    for path in glob.glob("{}/*.pkl".format(args.log_dir)):
        with open(path, 'rb') as f:
            args = torch.load(f)
            try:
                run = torch.load(f, map_location='cpu')
            except EOFError:
                continue

        if not f(run):
            print("remove {}".format(path))
            os.remove(path)


if __name__ == '__main__':
    main()
