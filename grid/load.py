# pylint: disable=missing-docstring, bare-except, invalid-name, line-too-long
import glob
import itertools
import os
import pickle
from collections import defaultdict, namedtuple

try:
    from tqdm.auto import tqdm
except ModuleNotFoundError:
    def tqdm(x):
        return x


Run = namedtuple('Run', 'file, time, args, data')
GLOBALCACHE = defaultdict(dict)


def load(directory, pred_args=None, pred_run=None, cache=True, extractor=None):
    return list(load_iter(directory, pred_args, pred_run, cache, extractor))


def load_iter(directory, pred_args=None, pred_run=None, cache=True, extractor=None):
    if extractor is not None:
        cache = False

    directory = os.path.normpath(directory)

    if not os.path.isdir(directory):
        raise NotADirectoryError('{} does not exists'.format(directory))

    cache_runs = GLOBALCACHE[directory] if cache else dict()

    for file in tqdm(sorted(glob.glob(os.path.join(directory, '*.pk')))):
        time = os.path.getctime(file)

        if file in cache_runs and time == cache_runs[file].time:
            x = cache_runs[file]

            if pred_args is not None and not pred_args(x.args):
                continue

            if pred_run is not None and not pred_run(x.data):
                continue

            yield x.data
            continue

        with open(file, 'rb') as f:
            try:
                args = pickle.load(f)

                if pred_args is not None and not pred_args(args):
                    continue

                data = pickle.load(f)
            except:
                continue

        if extractor is not None:
            data = extractor(data)

        x = Run(file=file, time=time, args=args, data=data)
        cache_runs[file] = x

        if pred_run is not None and not pred_run(x.data):
            continue

        yield x.data


def hashable(x):
    if isinstance(x, list):
        x = tuple(hashable(i) for i in x)
    if isinstance(x, set):
        x = frozenset(x)
    try:
        hash(x)
    except TypeError:
        return '<not hashable>'
    return x


def keyall(x):
    if x is None:
        return (0, x)
    if isinstance(x, bool):
        return (1, x)
    if isinstance(x, str):
        return (2, x)
    if isinstance(x, (int, float)):
        return (3, x)
    if isinstance(x, tuple):
        return (4, tuple(keyall(i) for i in x))
    if isinstance(x, list):
        return (5, [keyall(i) for i in x])
    return (6, x)


def args_intersection(argss):
    return {k: list(v)[0] for k, v in args_union(argss).items() if len(v) == 1}


def args_todict(r):
    if not isinstance(r, dict):
        r = r.__dict__
    return {
        key: hashable(value)
        for key, value in r.items()
        if key not in ['pickle', 'output']
    }


def args_union(argss):
    argss = [args_todict(r) for r in argss]
    keys = {key for r in argss for key in r.keys()}

    return {
        key: {r[key] if key in r else None for r in argss}
        for key in keys
    }


def args_diff(argss):
    args = args_intersection(argss)
    argss = [args_todict(r) for r in argss]
    return [
        {
            key: a[key]
            for key in a.keys()
            if key not in args.keys()
        }
        for a in argss
    ]


def load_grouped(directory, group_by, pred_args=None, pred_run=None):
    """

    example:

    args, groups = load_grouped('results', ['alpha', 'seed_init'])

    for param, rs in groups:
        # in `rs` only 'alpha' and 'seed_init' can vary
        plot(rs, label=param)

    """
    runs = load(directory, pred_args=pred_args, pred_run=pred_run)

    return group_runs(runs, group_by)


def group_runs(runs, group_by):
    args = args_intersection([r['args'] for r in runs])
    variants = {
        key: sorted(values, key=keyall)
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
                (hashable(getattr(r['args'], k)) == v) if hasattr(r['args'], k) else (v is None)
                for k, v in var.items()
            )
        ]
        if rs:
            groups.append((var, rs))
    assert len(runs) == sum(len(rs) for _a, rs in groups)

    return args, groups
