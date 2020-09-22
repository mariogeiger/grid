# pylint: disable=C,R,E1101
import argparse
import os
import time

import torch


def execute(args):
    for i in range(3):
        time.sleep(0.5)
        print("computation {} / 3".format(i + 1), flush=True)  # need flush=True

    result_of_heavy_computation = args.a / args.b

    return {
        'args': args,
        'division': result_of_heavy_computation
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pickle", type=str, required=True)
    parser.add_argument("--a", type=int, required=True)
    parser.add_argument("--b", type=int, required=True)

    args = parser.parse_args()

    torch.save(args, args.pickle, _use_new_zipfile_serialization=False)
    try:
        results = execute(args)

        with open(args.pickle, 'wb') as f:
            torch.save(args, f, _use_new_zipfile_serialization=False)
            torch.save(results, f, _use_new_zipfile_serialization=False)
    except:
        os.remove(args.pickle)
        raise


if __name__ == "__main__":
    main()
