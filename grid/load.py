# pylint: disable=missing-docstring, bare-except, invalid-name
import glob
import os
from collections import defaultdict, namedtuple

import torch

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    tqdm = lambda x: x


Run = namedtuple('Run', 'file, time, args, data')
GLOBALCACHE = defaultdict(dict)


def load(directory, predicate=None, cache=True):
    return list(load_iter(directory, predicate, cache))


def load_iter(directory, predicate=None, cache=True):
    directory = os.path.normpath(directory)

    if not os.path.isdir(directory):
        raise NotADirectoryError('{} does not exists'.format(directory))

    cache_runs = GLOBALCACHE[directory] if cache else dict()

    for file in tqdm(sorted(glob.glob(os.path.join(directory, '*.pkl')))):
        time = os.path.getctime(file)

        if file in cache_runs and time == cache_runs[file].time:
            x = cache_runs[file]

            if predicate is not None and not predicate(x.args):
                continue

            yield x.data
            continue

        with open(file, 'rb') as f:
            try:
                args = torch.load(f)

                if predicate is not None and not predicate(args):
                    continue

                data = torch.load(f, map_location='cpu')
            except:
                continue

        x = Run(file=file, time=time, args=args, data=data)
        cache_runs[file] = x
        yield x.data
