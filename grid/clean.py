import argparse
import glob
import os
from tqdm.auto import tqdm

from grid import load_file, to_dict


def unique_tuple(args):
    d = [(key, value) for key, value in to_dict(args).items() if key not in ['output']]
    return tuple(sorted(d))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    parser.add_argument("--pred_args", type=str)
    parser.add_argument("--pred_run", type=str)
    args = parser.parse_args()

    pred_args = eval(args.pred_args) if args.pred_args else None
    pred_run = eval(args.pred_run) if args.pred_run else None

    done = set()

    for path in tqdm(sorted(glob.glob("{}/*.pk".format(args.log_dir)))):
        f = load_file(path)

        try:
            args = next(f)
        except EOFError:
            print(f"rm empty args: {path}")
            os.remove(path)
            continue

        if pred_args is not None and not pred_args(args):
            print(f"pred_args failed: {path}")
            os.remove(path)
            continue

        try:
            run = next(f)
        except EOFError:
            print(f"rm empty data: {path}")
            os.remove(path)
            continue

        if pred_run is not None and not pred_run(run):
            print(f"pred_run failed: {path}")
            os.remove(path)
            continue

        targs = unique_tuple(args)
        if targs in done:
            print(f"rm clone: {path}")
            os.remove(path)
            continue

        done.add(targs)


if __name__ == '__main__':
    main()
