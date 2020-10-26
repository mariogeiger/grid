# pylint: disable=C
import argparse
import glob
import os
import random
from itertools import count

from grid.exec import load_args, load_data


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir_src", type=str)
    parser.add_argument("log_dir_dst", type=str)
    parser.add_argument("--pred_args", type=str)
    parser.add_argument("--pred_run", type=str)
    args = parser.parse_args()

    pred_args = eval(args.pred_args) if args.pred_args else None
    pred_run = eval(args.pred_run) if args.pred_run else None

    def tup(args):
        d = [(key, value) for key, value in args.__dict__.items() if key not in ['pickle', 'output']]
        return tuple(sorted(d))

    done_dst = {
        tup(load_args(f))
        for f in glob.glob("{}/*.pk".format(args.log_dir_dst))
    }

    for path_src in glob.glob("{}/*.pk".format(args.log_dir_src)):
        a = load_args(path_src)
        if pred_args is not None and not pred_args(a):
            print("{} skipped".format(path_src))
            continue

        if pred_run is not None and not pred_run(load_data(path_src)):
            print("{} skipped".format(path_src))
            continue

        args_src = tup(a)

        if args_src in done_dst:
            print("{} ok".format(path_src))
            continue

        for i in count(random.randint(0, 999_999)):
            i = i % 1_000_000
            name = "{:05d}.pk".format(i)
            path_dst = os.path.join(args.log_dir_dst, name)
            if not os.path.isfile(path_dst):
                break

        print("[{}] {} -> {}".format(
            " ".join("{}={}".format(key, value) for key, value in args_src),
            path_src, path_dst))
        os.rename(path_src, path_dst)

        done_dst.add(args_src)


if __name__ == '__main__':
    main()
