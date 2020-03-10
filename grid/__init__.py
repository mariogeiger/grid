# pylint: disable=missing-docstring, invalid-name
from .load import load, load_iter, load_grouped
from .info import print_info
from .gpu import get_free_gpus


__all__ = ['load', 'load_iter', 'load_grouped', 'print_info', 'get_free_gpus', 'args_intersection', 'args_union']


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


def args_intersection(argss):
    return {k: list(v)[0] for k, v in args_union(argss).items() if len(v) == 1}


def args_union(argss):
    argss = [
        {
            key: hashable(value)
            for key, value in r.__dict__.items()
            if key != 'pickle'
        }
        for r in argss
    ]

    keys = {key for r in argss for key in r.keys()}

    return {
        key: {r[key] if key in r else None for r in argss}
        for key in keys
    }
