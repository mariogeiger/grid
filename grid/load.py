# pylint: disable=missing-docstring, bare-except
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
    directory = os.path.normpath(directory)

    runs = GLOBALCACHE[directory] if cache else dict()

    for file in tqdm(sorted(glob.glob(os.path.join(directory, '*.pkl')))):
        time = os.path.getctime(file)

        if file in runs and time == runs[file].time:
            continue

        with open(file, 'rb') as f:
            try:
                args = torch.load(f)

                if predicate is not None and not predicate(args):
                    continue

                data = torch.load(f, map_location='cpu')
            except:
                continue

        runs[file] = Run(file=file, time=time, args=args, data=data)

    if cache:
        GLOBALCACHE[directory] = runs

    return [x.data for file, x in runs.items() if predicate is None or predicate(x.args)]
