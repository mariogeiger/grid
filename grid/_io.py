import glob
import os
import pickle
import time
from collections import defaultdict, namedtuple

from grid import args_intersection, args_union, keyall, to_dict

Run = namedtuple('Run', 'file, ctime, args, data')
GLOBALCACHE = defaultdict(dict)


def identity(x):
    return x


def deepmap(fun, data):
    if isinstance(data, (list, tuple, set, frozenset)):
        return type(data)(deepmap(fun, x) for x in data)

    if isinstance(data, dict):
        return {key: deepmap(fun, x) for key, x in data.items()}

    return fun(data)


def torch_to_numpy(data):
    import torch

    def fun(x):
        if isinstance(x, torch.Tensor):
            return x.numpy()
        else:
            return x
    return deepmap(fun, data)


def load_file(f):
    with open(f, 'rb') as rb:
        yield to_dict(pickle.load(rb))
        yield pickle.load(rb)


def load_args(f, sleep=0.01, trials=10):
    for _ in range(trials - 1):
        try:
            return next(load_file(f))
        except (pickle.PickleError, FileNotFoundError, EOFError):
            time.sleep(sleep)
    return next(load_file(f))


def load(directory, pred_args=None, pred_run=None, cache=True, extractor=None, convertion=None, tqdm=identity):
    return list(load_iter(directory, pred_args, pred_run, cache, extractor, convertion, tqdm=tqdm))


def load_iter(directory, pred_args=None, pred_run=None, cache=True, extractor=None, convertion=None, tqdm=identity):
    for d in directory.split(":"):
        for r in _load_iter(d, pred_args, pred_run, cache, extractor, convertion, tqdm):
            yield r


def _load_iter(directory, pred_args=None, pred_run=None, cache=True, extractor=None, convertion=None, tqdm=identity):
    if extractor is not None:
        cache = False

    directory = os.path.normpath(directory)

    if not os.path.isdir(directory):
        raise NotADirectoryError('{} does not exists'.format(directory))

    cache_runs = GLOBALCACHE[(directory, convertion)] if cache else dict()

    for file in tqdm(sorted(glob.glob(os.path.join(directory, '*.pk')))):
        ctime = os.path.getctime(file)

        if file in cache_runs and ctime == cache_runs[file].ctime:
            x = cache_runs[file]

            if pred_args is not None and not pred_args(x.args):
                continue

            if pred_run is not None and not pred_run(x.data):
                continue

            yield x.data
            continue

        try:
            f = load_file(file)
            args = next(f)

            if pred_args is not None and not pred_args(args):
                continue

            data = next(f)
        except (pickle.PickleError, FileNotFoundError, EOFError):
            continue

        if extractor is not None:
            data = extractor(data)

        if pred_run is not None and not pred_run(data):
            continue

        if convertion == 'torch_to_numpy':
            data = torch_to_numpy(data)
        elif convertion == 'args':
            data = args
        elif convertion == 'file_args':
            data = (file, args)
        else:
            assert convertion is None

        x = Run(file=file, ctime=ctime, args=args, data=data)
        cache_runs[file] = x

        yield x.data


def load_grouped(directory, group_by, pred_args=None, pred_run=None, convertion=None, tqdm=identity):
    """

    example:

    args, groups = load_grouped('results', ['alpha', 'seed_init'])

    for param, rs in groups:
        # in `rs` only 'alpha' and 'seed_init' can vary
        plot(rs, label=param)

    """
    runs = load(directory, pred_args=pred_args, pred_run=pred_run, convertion=convertion, tqdm=tqdm)

    return group_runs(runs, group_by, tqdm=tqdm)


def group_runs(runs, group_by, tqdm=identity):
    args = args_intersection([r['args'] for r in runs])
    variants = {
        key: sorted(values, key=keyall)
        for key, values in args_union([r['args'] for r in runs]).items()
        if len(values) > 1 and key not in group_by
    }
    keys = sorted(variants.keys())
    famillies = sorted({tuple(to_dict(r['args']).get(k, None) for k in keys) for r in runs}, key=keyall)

    groups = []
    for vals in tqdm(famillies):
        rs = [
            r
            for r in runs
            if all(
                to_dict(r['args']).get(k, None) == v
                for k, v in zip(keys, vals)
            )
        ]
        if rs:
            groups.append(({k: v for k, v in zip(keys, vals)}, rs))
    assert len(runs) == sum(len(rs) for _a, rs in groups)

    return args, groups
