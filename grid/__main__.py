# pylint: disable=W0221, C, R, W1202, E1101
'''
A script that perform grid parameters search in parallel

Usage:

   python grid.py --log_dir results --cmd PROGRAM --PAR1:int 1 2 3 --PAR2:float 0.5 1.2 --PAR3:str a b c


PROGRAM - it needs to accept the parameter "--pickle FILENAME" and it needs to save its passed arguments with `torch.save(args)`
PAR1, PAR2, PAR3 - parameters of the search grid, they are passed one by one to PROGRAM


python template for PROGRAM

    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("--pickle", type=str, required=True)
        # and many other arguments

        args = parser.parse_args()

        torch.save(args, args.pickle)
        try:
            results = execute(args)

            with open(args.pickle, 'wb') as f:
                torch.save(args, f)
                torch.save(results, f)
        except:
            os.remove(args.pickle)
            raise


Example:

    python grid.py --n_parallel 4 --sleep 10 --log_dir M8kP_sgd --cmd "grun python train3.py --desc \"10k is too large\" --pte 8000 --lr 0.01 --train_time 1200 --dataset mnist --bs 32 --data_seed 0 --ptr 8000" --init_seed:int 0 1 2 3 4 5 --h:int 43 39 36 33 30 28 25 23 21 20 18 17 15 14

'''
import argparse
import glob
import os
import random
import re
import subprocess
import time
from itertools import count, product

import torch


def main():
    parser = argparse.ArgumentParser("grid")


    parser.add_argument("--log_dir", type=str, required=True, help="path to a directory")
    parser.add_argument("--n_parallel", type=int, help="maximum parallel instances (infinite by default)")
    parser.add_argument("--sleep", type=float, default=0, help="sleep time between two runs (in seconds)")
    parser.add_argument("--cmd", type=str, required=True, help="program to execute in parallel for the grid search")  # srun --partition gpu --qos gpu --gres gpu:1 --time 3-00:00:00 --mem 12G --pty python train.py

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
                running = [x for x in running if x.poll() is None]
                time.sleep(2)

        for i in count(random.randint(0, 9999)):
            fn = "{:05d}.pkl".format(i)
            fp = os.path.join(args.log_dir, fn)
            if not os.path.isfile(fp):
                break

        cmd = command.format(pickle=fp, **{name: val for val, (name, type, vals) in zip(param, params)})

        running.append(subprocess.Popen(re.findall(r'\"[^\"]*\"|\S+', cmd)))
        print("[{}] {}".format(text, cmd))
        time.sleep(args.sleep)

    for x in running:
        x.wait()


if __name__ == '__main__':
    main()
