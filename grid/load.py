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
GLOBALCACHE = defaultdict(list)


def load(directory, predicate=None, cache=True):
    directory = os.path.normpath(directory)

    runs = GLOBALCACHE[directory] if cache else []
    files = {x.file: x.time for x in runs}

    for file in tqdm(sorted(glob.glob(os.path.join(directory, '*.pkl')))):
        time = os.path.getctime(file)

        if file in files and time == files[file]:
            continue

        with open(file, 'rb') as f:
            try:
                args = torch.load(f)

                if predicate is not None and not predicate(args):
                    continue

                data = torch.load(f, map_location='cpu')
            except:
                continue
        runs.append(Run(file=file, time=time, args=args, data=data))

    if cache:
        GLOBALCACHE[directory] = runs

    return [x.data for x in runs if predicate(x.args)]
