# pylint: disable=eval-used, missing-docstring, invalid-name, line-too-long
import argparse
import glob
import os

import torch

from grid import print_info, zip_load

try:
    from tqdm.auto import tqdm
except ModuleNotFoundError:
    def tqdm(x):
        return x


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    parser.add_argument("--thr", type=int, default=5)
    parser.add_argument("--pred", type=str)
    args = parser.parse_args()

    pred_args = eval(args.pred) if args.pred else None

    if os.path.isfile("{}/info".format(args.log_dir)):
        with open("{}/info".format(args.log_dir), 'rb') as f:
            info = torch.load(f)
            print("last command")
            if 'cmd' in info:
                print(info['cmd'])
            print("git commit    {}".format(info['git']['log']))
            print("git status    {}".format(info['git']['status']))

    argss = [torch.load(path) for path in tqdm(glob.glob("{}/*.pkl".format(args.log_dir)))]
    argss += [zip_load(path, 'args') for path in tqdm(glob.glob("{}/*.zip".format(args.log_dir)))]
    argss = [a for a in argss if a is not None]
    argss = [a for a in argss if pred_args is None or pred_args(a)]

    print_info(argss, args.thr)


if __name__ == '__main__':
    main()
