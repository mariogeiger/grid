# pylint: disable=missing-docstring, invalid-name, line-too-long, bare-except
import datetime
import glob
import os
import pickle
import random
import re
import shlex
import subprocess
import threading
import time
from itertools import count, product

try:
    from tqdm.auto import tqdm
except ModuleNotFoundError:
    def tqdm(x):
        return x


def load_args(f):
    for _ in range(5):
        try:
            with open(f, 'rb') as rb:
                return pickle.load(rb)
        except:
            time.sleep(0.1)
    with open(f, 'rb') as rb:
        return pickle.load(rb)


def to_dict(x):
    if isinstance(x, dict):
        return x

    return x.__dict__


def load_data(f):
    for _ in range(5):
        try:
            with open(f, 'rb') as rb:
                pickle.load(rb)
                return pickle.load(rb)
        except:
            time.sleep(0.1)
    with open(f, 'rb') as rb:
        pickle.load(rb)
        return pickle.load(rb)


def print_output(out, text, path):
    if path is not None:
        open(path, 'ta').close()

    for line in iter(out.readline, b''):
        output = line.decode("utf-8")
        m = re.findall(r"job (\d+)", output)  # srun: job (\d+) has been allocated resources
        if m and len(text) < 2:
            text.insert(0, m[0])

        print("[{}] {}".format(" ".join(text), output), end="")

        if path is not None:
            with open(path, 'ta') as f:
                f.write("{} [{}] {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), " ".join(text), line.decode("utf-8")))

    if path is None:
        print("[{}] terminated".format(" ".join(text)))


def exec_grid(log_dir, cmd, params, sleep=0, n=None):
    command = "{} --output {{output}}".format(cmd)

    for name, _vals in params:
        command += " --{0} {{{0}}}".format(name)

    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    with open(os.path.join(log_dir, "info"), 'wb') as f:
        pickle.dump({
            'cmd': cmd,
            'params': params,
            'git': {
                'log': subprocess.getoutput('git log --format="%H" -n 1 -z'),
                'status': subprocess.getoutput('git status -z'),
            }
        }, f)

    done_files = set()
    done_param = dict()

    for f in tqdm(glob.glob(os.path.join(log_dir, "*.pk"))):
        if f not in done_files:
            done_files.add(f)

            a = to_dict(load_args(f))
            a = tuple((name, a[name] if name in a else None) for name, _vals in params)
            done_param[a] = f

    running = []
    threads = []

    for param in product(*[vals for name, vals in params]):
        param = tuple((name, val) for val, (name, vals) in zip(param, params))

        if len(running) > 0:
            time.sleep(sleep)

        if n is not None:
            while len(running) >= n:
                running = [x for x in running if x.poll() is None]
                time.sleep(0.2)

        if os.path.isfile('stop'):
            print()
            print('  >> stop file detected!  <<')
            print()
            break

        for f in glob.glob(os.path.join(log_dir, "*.pk")):
            if f not in done_files:
                done_files.add(f)

                a = to_dict(load_args(f))
                a = tuple((name, a[name] if name in a else None) for name, _vals in params)
                done_param[a] = f

        text = " ".join("{}={}".format(name, val) for name, val in param)

        if param in done_param:
            print('[{}] {}'.format(text, done_param[param]))
            continue

        for i in count(random.randint(0, 999_999)):
            i = i % 1_000_000
            fn = "{:06d}.pk".format(i)
            fp = os.path.join(log_dir, fn)
            if not os.path.isfile(fp):
                break

        text = "{} {}".format(fp, text)
        text = [text]

        cmd = command.format(output=fp, **dict(param))

        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        t = threading.Thread(target=print_output, args=(p.stdout, text, None))
        t.daemon = True
        t.start()
        threads.append(t)
        t = threading.Thread(target=print_output, args=(p.stderr, text, os.path.join(log_dir, 'stderr')))
        t.daemon = True
        t.start()
        threads.append(t)

        running.append(p)
        print("[{}] {}".format(" ".join(text), cmd))

    for x in running:
        x.wait()

    for t in threads:
        t.join()


def exec_blocking(log_dir, cmd, param):
    command = "{} --output {{output}}".format(cmd)

    for name, _val in param:
        command += " --{0} {{{0}}}".format(name)

    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    done_files = set()
    done_param = dict()

    for f in tqdm(glob.glob(os.path.join(log_dir, "*.pk"))):
        if f not in done_files:
            done_files.add(f)

            a = load_args(f)
            a = tuple((name, getattr(a, name) if hasattr(a, name) else None) for name, _val in param)
            done_param[a] = f

    if param in done_param:
        f = done_param[param]
        while True:
            try:
                r = load_data(f)
            except EOFError:
                time.sleep(1)
            else:
                return r

    for i in count(random.randint(0, 999_999)):
        i = i % 1_000_000
        fn = "{:06d}.pk".format(i)
        fp = os.path.join(log_dir, fn)
        if not os.path.isfile(fp):
            break

    cmd = command.format(output=fp, **dict(param))

    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    text = " ".join("{}={}".format(name, val) for name, val in param)

    t1 = threading.Thread(target=print_output, args=(p.stdout, text, None))
    t1.daemon = True
    t1.start()
    t2 = threading.Thread(target=print_output, args=(p.stderr, text, os.path.join(log_dir, 'stderr')))
    t2.daemon = True
    t2.start()

    p.wait()
    t1.join()
    t2.join()

    return load_data(fp)
