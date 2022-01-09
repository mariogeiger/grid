# pylint: disable=missing-docstring
import argparse
import os
import time
import pickle


def execute(args):
    for i in range(3):
        time.sleep(0.5)
        print("computation {} / 3".format(i + 1), flush=True)  # need flush=True

    result_of_heavy_computation = args["a"] / args["b"]

    return {
        'args': args,
        'division': result_of_heavy_computation
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--a", type=int, required=True)
    parser.add_argument("--b", type=int, required=True)

    args = parser.parse_args().__dict__

    with open(args["output"], 'wb') as handle:
        pickle.dump(args, handle)
    try:
        data = execute(args)
        with open(args["output"], 'wb') as handle:
            pickle.dump(args, handle)
            pickle.dump(data, handle)
    except:
        os.remove(args["output"])
        raise


if __name__ == "__main__":
    main()
