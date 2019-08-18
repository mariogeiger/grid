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
globalcache = defaultdict(list)


def load(directory, cache=False):
    directory = os.path.normpath(directory)

    runs = globalcache[directory] if cache else []
    files = {x.file: x.time for x in runs}

    for file in tqdm(sorted(glob.glob(os.path.join(directory, '*.pkl')))):
        time = os.path.getctime(file)

        if file in files and time == files[file]:
            continue

        with open(file, 'rb') as f:
            try:
                args = torch.load(f)
                data = torch.load(f, map_location='cpu')
            except:
                continue
        runs.append(Run(file=file, time=time, args=args, data=data))

    if cache:
        globalcache[directory] = runs

    return [x.data for x in runs]
