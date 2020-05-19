# pylint: disable=eval-used, missing-docstring, invalid-name, line-too-long


def print_info(argss, thr=5):
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

    def keyf(key):
        return (len({r[key] if key in r else None for r in argss}), key)

    for key in sorted({key for r in argss for key in r.keys()}, key=keyf):

        values = {r[key] if key in r else None for r in argss}
        values = [(x, len([1 for r in argss if (x is None and key not in r) or (key in r and r[key] == x)])) for x in values]
        n = len(values)

        try:
            values = sorted(values)
        except TypeError:
            pass

        if n == 1:
            text = " ".join(["{}".format(repr(x)) for x, m in values])
            print("{}: {}".format(key, text))
        elif n <= thr:
            text = " ".join(["{}({} runs)".format(repr(x), m) for x, m in values])
            print("{}: {}".format(key, text))
        else:
            text = " ".join([repr(x) for x, m in values])
            print("{}: ({} values) {}".format(key, n, text))

    print("{} records in total (some can be empty!)".format(len(argss)))
