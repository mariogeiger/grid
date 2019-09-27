# pylint: disable=C, eval-used
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
    parser.add_argument("filter", type=str)
    args = parser.parse_args()

    f = eval(args.filter)

    for path in tqdm(glob.glob("{}/*.pkl".format(args.log_dir))):
        if not f(torch.load(path)):
            print("remove {}".format(path))
            os.remove(path)


if __name__ == '__main__':
    main()
