# pylint: disable=missing-docstring, bare-except, invalid-name
import glob
import itertools
import os
from collections import defaultdict, namedtuple

import torch

from . import args_intersection, args_union

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    def tqdm(x):
        return x


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


def load_grouped(directory, group_by, pred_args=None, pred_run=None):
    """

    example:

    args, groups = load_grouped('results', ['alpha', 'seed_init'])

    for param, rs in groups:
        # in `rs` only 'alpha' and 'seed_init' can vary
        plot(rs, label=param)

    """
    runs = load(directory, predicate=pred_args)
    if pred_run is not None:
        runs = [r for r in runs if pred_run(r)]

    args = args_intersection([r['args'] for r in runs])
    variants = {
        key: sorted(values)
        for key, values in args_union([r['args'] for r in runs]).items()
        if len(values) > 1 and key not in group_by
    }

    groups = []
    for vals in itertools.product(*variants.values()):
        var = {k: v for k, v in zip(variants, vals)}

        rs = [
            r
            for r in runs
            if all(
                (getattr(r['args'], k) == v) if hasattr(r['args'], k) else (v is None)
                for k, v in var.items()
            )
        ]
        if rs:
            groups.append((var, rs))

    return args, groups
