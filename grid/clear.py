# pylint: disable=eval-used, missing-docstring, invalid-name, line-too-long
import argparse
import glob
import io
import os
import pickle
import time
import zipfile
from grid.exec import load_args, load_data

import torch


def zip_load(path, key):
    if not os.path.isfile(path):
        return None
    for _ in range(10):
        try:
            with zipfile.ZipFile(path, 'r') as zf:
                if key in zf.namelist():
                    with zf.open(key, 'r') as f:
                        return torch.load(io.BytesIO(f.read()), map_location='cpu')
        except zipfile.BadZipFile:
            time.sleep(1)
    return None


def zip_save(path, dict_data):
    with zipfile.ZipFile(path, 'w') as zf:
        for key, data in dict_data.items():
            f = io.BytesIO()
            torch.save(data, f)
            zf.writestr(key, f.getbuffer())


try:
    from tqdm.auto import tqdm
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
        d = [(key, value) for key, value in args.__dict__.items() if key not in ['pickle', 'output']]
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

        with open(path.replace('pkl', 'pk'), 'wb') as f:
            pickle.dump(args, f)
            pickle.dump(run, f)
        os.remove(path)

        done.add(args)

    done = set()

    for path in tqdm(sorted(glob.glob("{}/*.zip".format(args.log_dir)))):
        args = zip_load(path, 'args')

        if args is None:
            print("args None: {}".format(path))
            os.remove(path)
            continue

        if pred_args and not pred_args(args):
            print("pred_args failed: {}".format(path))
            os.remove(path)
            continue

        run = zip_load(path, 'data')

        if run is None:
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

        with open(path.replace('zip', 'pk'), 'wb') as f:
            pickle.dump(args, f)
            pickle.dump(run, f)
        os.remove(path)

        done.add(args)

    done = set()

    for path in tqdm(sorted(glob.glob("{}/*.pk".format(args.log_dir)))):
        args = load_args(path)

        if pred_args and not pred_args(args):
            print("pred_args failed: {}".format(path))
            os.remove(path)
            continue

        try:
            run = load_data(path)
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
