# pylint: disable=missing-docstring
from .load import load, load_iter
from .info import print_info
from .gpu import get_free_gpus


def args_intersection(argss):
    from functools import reduce

    def hashable(x):
        if isinstance(x, list):
            x = tuple(x)
        if isinstance(x, set):
            x = frozenset(x)
        try:
            hash(x)
        except TypeError:
            return '<not hashable>'
        return x

    argss = [
        {
            key: hashable(value)
            for key, value in r.__dict__.items()
            if key != 'pickle'
        }
        for r in argss
    ]

    keys = reduce(set.intersection, [set(r.keys()) for r in argss])

    values = {k: {r[k] for r in argss} for k in keys}
    return {k: list(v)[0] for k, v in values.items() if len(v) == 1}
