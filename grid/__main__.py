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

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    def tqdm(x):
        return x


def print_output(out, text, path):
    if path is not None:
        open(path, 'ta').close()

    for line in iter(out.readline, b''):
        print("[{}] {}".format(text, line.decode("utf-8")), end="")

        if path is not None:
            with open(path, 'ta') as f:
                f.write("{} [{}] {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), text, line.decode("utf-8")))

    if path is None:
        print("[{}] terminated".format(text))


def main():
    parser = argparse.ArgumentParser("grid")
    parser.add_argument("log_dir", type=str, help="path to a directory")
    parser.add_argument("cmd", type=str, help="program to execute in parallel for the grid search")
    parser.add_argument("--n", type=int, help="maximum parallel instances (infinite by default)")
    parser.add_argument("--sleep", type=float, default=0, help="sleep time between two runs (in seconds)")
    args, argv = parser.parse_known_args()

    command = "{} --pickle {{pickle}}".format(args.cmd)

    params = []
    for x in argv:
        if x.startswith('--'):
            if ':' in x:
                name, typ = x[2:].split(':')
                typ = eval(typ)
            else:
                name = x[2:]
                typ = None
            params.append((name, typ, [], set()))
            command += " --{0} {{{0}}}".format(name)
        else:
            name, typ, vals, opt = params[-1]
            if x in ["-r"]:
                opt.add(x)
            else:
                if typ is None:
                    vals.append(eval(x))
                else:
                    vals.append(typ(x))

    if not os.path.isdir(args.log_dir):
        os.mkdir(args.log_dir)

    with open(os.path.join(args.log_dir, "info"), 'ab') as f:
        torch.save({
            'args': args,
            'params': params,
            'git': {
                'log': subprocess.getoutput('git log --format="%H" -n 1 -z'),
                'status': subprocess.getoutput('git status -z'),
            }
        }, f)

    done_files = set()
    done_param = dict()

    for f in tqdm(glob.glob(os.path.join(args.log_dir, "*.pkl"))):
        if f not in done_files:
            done_files.add(f)

            a = torch.load(f)
            a = tuple(getattr(a, name) if hasattr(a, name) else None for name, _typ, vals, _opt in params)
            done_param[a] = f

    running = []
    threads = []

    for param in product(*[reversed(vals) if "-r" in opt else vals for name, _typ, vals, opt in params]):
        if len(running) > 0:
            time.sleep(args.sleep)

        if args.n is not None:
            while len(running) >= args.n:
                running = [x for x in running if x.poll() is None]
                time.sleep(0.2)

        if os.path.isfile('stop'):
            print()
            print('  >> stop file detected!  <<')
            print()
            break

        for f in glob.glob(os.path.join(args.log_dir, "*.pkl")):
            if f not in done_files:
                done_files.add(f)

                a = torch.load(f)
                a = tuple(getattr(a, name) if hasattr(a, name) else None for name, _typ, vals, _opt in params)
                done_param[a] = f

        text = " ".join("{}={}".format(name, val) for val, (name, _typ, vals, _opt) in zip(param, params))

        if param in done_param:
            print('[{}] {}'.format(text, done_param[param]))
            continue

        for i in count(random.randint(0, 50000)):
            fn = "{:05d}.pkl".format(i)
            fp = os.path.join(args.log_dir, fn)
            if not os.path.isfile(fp):
                break

        cmd = command.format(pickle=fp, **{name: val for val, (name, _typ, vals, _opt) in zip(param, params)})

        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        t = threading.Thread(target=print_output, args=(p.stdout, text, None))
        t.daemon = True
        t.start()
        threads.append(t)
        t = threading.Thread(target=print_output, args=(p.stderr, text, os.path.join(args.log_dir, 'stderr')))
        t.daemon = True
        t.start()
        threads.append(t)

        running.append(p)
        print("[{}] {}".format(text, cmd))

    for x in running:
        x.wait()

    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
