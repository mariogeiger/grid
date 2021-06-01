# pylint: disable=eval-used, missing-docstring, invalid-name, line-too-long
import argparse
import glob
import os
import pickle
from tqdm.auto import tqdm
from grid import to_dict, args_hash_able


def print_info(argss, thr=5):
    argss = [args_hash_able(to_dict(r)) for r in argss]

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
        try:
            with open("{}/info".format(args.log_dir), 'rb') as f:
                info = pickle.load(f)
        except:
            pass
        else:
            if isinstance(info, dict):
                print("last command")
                if 'cmd' in info:
                    print(info['cmd'])
                print("git commit    {}".format(info['git']['log']))
                print("git status    {}".format(info['git']['status']))

    argss = [pickle.load(open(path, 'rb')) for path in tqdm(glob.glob("{}/*.pk".format(args.log_dir)))]
    argss = [a for a in argss if a is not None]
    argss = [a for a in argss if pred_args is None or pred_args(a)]

    print_info(argss, args.thr)


if __name__ == '__main__':
    main()
