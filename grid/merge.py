import argparse
import glob
import os

from grid import load_file, load_args, new_filename


def to_dict(a):
    if not isinstance(a, dict):
        return a.__dict__
    return a


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
        d = [(key, value) for key, value in to_dict(args).items() if key not in ['pickle', 'output']]
        return tuple(sorted(d))

    done_dst = {
        tup(load_args(f))
        for f in glob.glob("{}/*.pk".format(args.log_dir_dst))
    }

    for path_src in sorted(glob.glob("{}/*.pk".format(args.log_dir_src))):
        f = load_file(path_src)
        a = next(f)
        if pred_args is not None and not pred_args(a):
            print("{} skipped".format(path_src))
            continue

        if pred_run is not None and not pred_run(next(f)):
            print("{} skipped".format(path_src))
            continue

        args_src = tup(a)

        if args_src in done_dst:
            print("{} ok".format(path_src))
            continue

        path_dst = new_filename(args.log_dir_dst)

        print("{} -> {}".format(path_src, path_dst))
        os.rename(path_src, path_dst)

        done_dst.add(args_src)


if __name__ == '__main__':
    main()
