def to_dict(a):
    if not isinstance(a, dict):
        return a.__dict__
    return a


def hash_able(x):
    if isinstance(x, list):
        x = tuple(hash_able(i) for i in x)
    if isinstance(x, set):
        x = frozenset(x)
    try:
        hash(x)
    except TypeError:
        return "<not hashable>"
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


def args_hash_able(r):
    return {key: hash_able(value) for key, value in r.items() if key not in ["output"]}


def args_union(argss):
    argss = [args_hash_able(to_dict(r)) for r in argss]
    keys = {key for r in argss for key in r.keys()}

    return {key: {r[key] if key in r else None for r in argss} for key in keys}


def args_diff(argss):
    args = args_intersection(argss)
    argss = [args_hash_able(to_dict(r)) for r in argss]
    return [{key: a[key] for key in a.keys() if key not in args.keys()} for a in argss]
