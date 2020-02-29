# pylint: disable=eval-used, missing-docstring, invalid-name
import argparse
import glob
import os

import torch

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    def tqdm(x):
        return x


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    parser.add_argument("--pred_args", type=str)
    parser.add_argument("--pred_run", type=str)
    args = parser.parse_args()

    pred_args = eval(args.pred_args) if args.pred_args else None
    pred_run = eval(args.pred_run) if args.pred_run else None

    def tup(args):
        d = [(key, value) for key, value in args.__dict__.items() if key != 'pickle']
        return tuple(sorted(d))

    done = set()

    for path in tqdm(sorted(glob.glob("{}/*.pkl".format(args.log_dir)))):
        with open(path, 'rb') as f:
            args = torch.load(f)

            if pred_args and not pred_args(args):
                print("pred_args failed: {}".format(path))
                os.remove(path)
                continue

            try:
                run = torch.load(f, map_location='cpu')
            except EOFError:
                print("rm empty: {}".format(path))
                os.remove(path)
                continue

            if pred_run and not pred_run(run):
                print("pred_run failed: {}".format(path))
                os.remove(path)
                continue

            args = tup(args)
            if args in done:
                print("rm clone: {}".format(path))
                os.remove(path)
                continue

            done.add(args)


if __name__ == '__main__':
    main()
