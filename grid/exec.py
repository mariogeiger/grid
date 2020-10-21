# pylint: disable=missing-docstring, invalid-name, line-too-long
import datetime
import glob
import io
import os
import random
import shlex
import subprocess
import threading
import time
import zipfile
from itertools import count, product

import torch

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    def tqdm(x):
        return x


def zip_load(path, key):
    if not os.path.isfile(path):
        return None
    with zipfile.ZipFile(path, 'r') as zf:
        if key in zf.namelist():
            with zf.open(key, 'r') as f:
                return torch.load(io.BytesIO(f.read()), map_location='cpu')
    return None


def zip_save(path, dict_data):
    with zipfile.ZipFile(path, 'w') as zf:
        for key, data in dict_data.items():
            f = io.BytesIO()
            torch.save(data, f)
            zf.writestr(key, f.getbuffer())


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


def exec_grid(log_dir, cmd, params, sleep=0, n=None):
    command = "{} --output {{output}}".format(cmd)

    for name, _vals in params:
        command += " --{0} {{{0}}}".format(name)

    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    with open(os.path.join(log_dir, "info"), 'wb') as f:
        torch.save({
            'cmd': cmd,
            'params': params,
            'git': {
                'log': subprocess.getoutput('git log --format="%H" -n 1 -z'),
                'status': subprocess.getoutput('git status -z'),
            }
        }, f)

    done_files = set()
    done_param = dict()

    for f in tqdm(glob.glob(os.path.join(log_dir, "*.zip"))):
        if f not in done_files:
            done_files.add(f)

            a = zip_load(f, "args")
            a = tuple((name, getattr(a, name) if hasattr(a, name) else None) for name, _vals in params)
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

        for f in glob.glob(os.path.join(log_dir, "*.zip")):
            if f not in done_files:
                done_files.add(f)

                a = zip_load(f, "args")
                a = tuple((name, getattr(a, name) if hasattr(a, name) else None) for name, _vals in params)
                done_param[a] = f

        text = " ".join("{}={}".format(name, val) for name, val in param)

        if param in done_param:
            print('[{}] {}'.format(text, done_param[param]))
            continue

        for i in count(random.randint(0, 999990)):
            fn = "{:06d}.zip".format(i)
            fp = os.path.join(log_dir, fn)
            if not os.path.isfile(fp):
                break

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
        print("[{}] {}".format(text, cmd))

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

    for f in tqdm(glob.glob(os.path.join(log_dir, "*.zip"))):
        if f not in done_files:
            done_files.add(f)

            a = zip_load(f, "args")
            a = tuple((name, getattr(a, name) if hasattr(a, name) else None) for name, _val in param)
            done_param[a] = f

    if param in done_param:
        f = done_param[param]
        while True:
            data = zip_load(f, 'data')
            if data is not None:
                return data
            time.sleep(1)

    for i in count(random.randint(0, 999990)):
        fn = "{:06d}.zip".format(i)
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

    return zip_load(fp, 'data')
