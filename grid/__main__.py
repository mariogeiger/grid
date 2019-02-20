# pylint: disable=W0221, C, R, W1202, E1101
import argparse
import datetime
import glob
import os
import random
import re
import shlex
import subprocess
import time
from itertools import count, product

import torch


def print_outputs(args, processes):
    for text, x in processes:
        if x.stdout.closed:
            continue

        try:
            outs, errs = x.communicate(timeout=0.01)
            for line in outs.split(b'\n'):
                print("[{}] {}".format(text, line.decode("utf-8")))

            if len(errs) > 0:
                with open(os.path.join(args.log_dir, "stderr"), 'ta') as f:
                    for line in errs.split(b'\n'):
                        line = "{} [{}] {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), text, line.decode("utf-8"))
                        print(line)
                        f.write(line + '\n')

        except subprocess.TimeoutExpired:
            pass

    for text, x in processes:
        if x.poll() is not None:
            print("[{}] terminated with code {}".format(text, x.poll()))


def main():
    parser = argparse.ArgumentParser("grid")
    parser.add_argument("log_dir", type=str, help="path to a directory")
    parser.add_argument("cmd", type=str, help="program to execute in parallel for the grid search")
    parser.add_argument("--n_parallel", type=int, help="maximum parallel instances (infinite by default)")
    parser.add_argument("--sleep", type=float, default=0, help="sleep time between two runs (in seconds)")
    args, argv = parser.parse_known_args()

    command = "{} --pickle {{pickle}}".format(args.cmd)

    params = []
    for x in argv:
        if x.startswith('--'):
            name, type = x[2:].split(':')
            type = eval(type)
            params.append((name, type, []))
            command += " --{0} {{{0}}}".format(name)
        else:
            name, type, vals = params[-1]
            vals.append(type(x))

    if not os.path.isdir(args.log_dir):
        os.mkdir(args.log_dir)

    done_args = {f: torch.load(f) for f in glob.glob("{}/*.pkl".format(args.log_dir))}
    done_param = {tuple(getattr(args, name) for name, type, vals in params) for f, args in done_args.items()}

    running = []

    for param in product(*[vals for name, type, vals in params]):

        text = " ".join("{}={}".format(name, val) for val, (name, type, vals) in zip(param, params))

        for f in glob.glob("{}/*.pkl".format(args.log_dir)):
            if f not in done_args:
                a = torch.load(f)
                done_args[f] = a
                done_param.add(tuple(getattr(a, name) for name, type, vals in params))

        if param in done_param:
            print('[{}] already done'.format(text))
            continue

        if args.n_parallel is not None:
            while len(running) >= args.n_parallel:
                print_outputs(args, running)
                running = [(text, x) for text, x in running if x.poll() is None]
                time.sleep(0.2)

        for i in count(random.randint(0, 9999)):
            fn = "{:05d}.pkl".format(i)
            fp = os.path.join(args.log_dir, fn)
            if not os.path.isfile(fp):
                break

        cmd = command.format(pickle=fp, **{name: val for val, (name, type, vals) in zip(param, params)})

        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        running.append((text, p))
        print("[{}] {}".format(text, cmd))

        for _ in range(int(args.sleep / 0.2)):
            print_outputs(args, running)
            running = [(text, x) for text, x in running if x.poll() is None]
            time.sleep(0.2)


    while len(running) > 0:
        print_outputs(args, running)
        running = [(text, x) for text, x in running if x.poll() is None]
        time.sleep(0.2)


if __name__ == '__main__':
    main()
