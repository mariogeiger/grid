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

    fil = eval(args.filter)

    for path in tqdm(glob.glob("{}/*.pkl".format(args.log_dir))):
        with open(path, 'rb') as f:
            args = torch.load(f)
            try:
                run = torch.load(f, map_location='cpu')
            except EOFError:
                continue

        if not fil(run):
            print("remove {}".format(path))
            os.remove(path)


if __name__ == '__main__':
    main()
