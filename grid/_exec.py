import datetime
import glob
import os
import pickle
import random
import re
import shlex
import subprocess
import threading
import math
import time
from itertools import count, product
from grid import load_file, load_args, to_dict


def identity(x):
    return x


def launch_command(cmd, prefix, stderr_filename):
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    text = [prefix]

    t1 = threading.Thread(target=print_output, args=(p.stdout, text, None))
    t1.daemon = True
    t1.start()

    t2 = threading.Thread(target=print_output, args=(p.stderr, text, stderr_filename))
    t2.daemon = True
    t2.start()

    return p, t1, t2


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


def new_filename(log_dir):
    for i in count(random.randint(0, 999_999)):
        i = i % 1_000_000
        fn = "{:06d}.pk".format(i)
        fp = os.path.join(log_dir, fn)
        if not os.path.isfile(fp):
            return fp


def is_integer(x):
    return abs(round(x) - x) < 1e-6


def format_value(val):
    if isinstance(val, (float, int)):
        if is_integer(val) and val < 50:
            return str(int(val))
        if is_integer(math.log10(val)):
            return f"10**{round(math.log10(val))}"
        if is_integer(math.log2(val)):
            return f"2**{round(math.log2(val))}"
    return str(val)


def exec_grid(log_dir, cmd, params, sleep=0, n=None, tqdm=identity):
    command = f"{cmd} --output {{output}}"

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
            print(flush=True)
            print('  >> stop file detected!  <<', flush=True)
            print(flush=True)
            break

        for f in glob.glob(os.path.join(log_dir, "*.pk")):
            if f not in done_files:
                done_files.add(f)

                a = to_dict(load_args(f))
                a = tuple((name, a[name] if name in a else None) for name, _vals in params)
                done_param[a] = f

        param_str = " ".join(f"{name}={format_value(val)}" for name, val in param)

        if param in done_param:
            print(f'[{param_str}] {done_param[param]}', flush=True)
            continue

        fp = new_filename(log_dir)
        cmd = command.format(output=fp, **dict(param))

        p, t1, t2 = launch_command(cmd, f"{fp} {param_str}", os.path.join(log_dir, 'stderr'))
        running.append(p)
        threads += [t1, t2]

        print(f"[{fp} {param_str}] {cmd}", flush=True)

    for x in running:
        x.wait()

    for t in threads:
        t.join()


class Job:
    def __init__(self, f, p, t1, t2):
        self.f = f
        self.p = p
        self.t1 = t1
        self.t2 = t2

    def finished(self):
        return self.p is None or self.p.poll() is not None

    def running(self):
        return self.p is not None and self.p.poll() is None

    def wait(self):
        if self.p is not None:
            self.p.wait()
        if self.t1 is not None:
            self.t1.join()
        if self.t2 is not None:
            self.t2.join()

    def load(self):
        self.wait()

        while True:
            try:
                _, r = load_file(self.f)
            except EOFError:
                time.sleep(1)
            else:
                return r


def exec_one(log_dir, cmd, param, tqdm=identity):
    """Execute a single command with a list of parameters.

    Args:
        log_dir (str): The directory to store the output.
        cmd (str): The command to execute.
        param (tuple): A tuple of tuples (name, parameter) to pass to the command.
        tqdm (callable): A progress bar.

    Returns:
        A Job object.
    """
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    for f in tqdm(glob.glob(os.path.join(log_dir, "*.pk"))):
        a = to_dict(load_args(f))
        a = tuple((name, a[name] if name in a else None) for name, _val in param)

        if param == a:
            return Job(f, None, None, None)

    fp = new_filename(log_dir)
    command = f"{cmd} --output {fp}"

    for name, value in param:
        command += f" --{name} {value}"

    p, t1, t2 = launch_command(
        command,
        " ".join("{}={}".format(name, format_value(val)) for name, val in param),
        os.path.join(log_dir, 'stderr')
    )
    return Job(fp, p, t1, t2)
