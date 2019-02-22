# pylint: disable=W0221, C, R, W1202, E1101, eval-used
import argparse
import datetime
import glob
import os
import random
import shlex
import subprocess
import threading
import time
from itertools import count, product

import torch


def print_output(out, text, path):
    for line in iter(out.readline, b''):
        print("[{}] {}".format(text, line.decode("utf-8")), end="")

        if path is not None:
            with open(path, 'ta') as f:
                f.write("{} [{}] {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), text, line.decode("utf-8")))
    out.close()


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
            name, typ = x[2:].split(':')
            typ = eval(typ)
            params.append((name, typ, []))
            command += " --{0} {{{0}}}".format(name)
        else:
            name, typ, vals = params[-1]
            vals.append(typ(x))

    if not os.path.isdir(args.log_dir):
        os.mkdir(args.log_dir)

    done_args = {f: torch.load(f) for f in glob.glob("{}/*.pkl".format(args.log_dir))}
    done_param = {tuple(getattr(args, name) for name, _typ, vals in params) for f, args in done_args.items()}

    running = []

    for param in product(*[vals for name, _typ, vals in params]):

        text = " ".join("{}={}".format(name, val) for val, (name, _typ, vals) in zip(param, params))

        for f in glob.glob("{}/*.pkl".format(args.log_dir)):
            if f not in done_args:
                a = torch.load(f)
                done_args[f] = a
                done_param.add(tuple(getattr(a, name) for name, _typ, vals in params))

        if param in done_param:
            print('[{}] already done'.format(text))
            continue

        if args.n_parallel is not None:
            while len(running) >= args.n_parallel:
                running = [x for x in running if x.poll() is None]
                time.sleep(0.2)

        for i in count(random.randint(0, 50000)):
            fn = "{:05d}.pkl".format(i)
            fp = os.path.join(args.log_dir, fn)
            if not os.path.isfile(fp):
                break

        cmd = command.format(pickle=fp, **{name: val for val, (name, _typ, vals) in zip(param, params)})

        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        t = threading.Thread(target=print_output, args=(p.stdout, text, None))
        t.daemon = True
        t.start()
        t = threading.Thread(target=print_output, args=(p.stderr, text, os.path.join(args.log_dir, 'stderr')))
        t.daemon = True
        t.start()

        running.append(p)
        print("[{}] {}".format(text, cmd))

        time.sleep(args.sleep)


    for x in running:
        x.wait()


if __name__ == '__main__':
    main()
