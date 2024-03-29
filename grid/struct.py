import argparse
import json

import numpy as np

from grid import load_iter


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class Data:
    def __repr__(self):
        return "<data>"

    def __eq__(self, other):
        return True


def get_structure(r):
    if isinstance(r, dict):
        d = {key: get_structure(val) for key, val in r.items()}
        nb = sum(nb for nb, _ in d.values())
        return (nb, d)

    if isinstance(r, list):
        out = []
        count = []
        nb = 0
        for x in r:
            x = get_structure(x)
            nb += x[0]
            if x in out:
                count[out.index(x)] += 1
            else:
                out.append(x)
                count.append(1)
        return (nb, [count, out])

    if isinstance(r, tuple):
        t = tuple(get_structure(x) for x in r)
        nb = sum(nb for nb, _ in t)
        return (nb, t)

    if isinstance(r, (int, float)):
        return (8, "number")

    import torch

    if isinstance(r, torch.Tensor) and r.grad_fn is not None:
        print("detected tensor with tree ", r.grad_fn)
        nb = r.numel() * r.element_size()
        return (nb, "tensor with tree!")

    if isinstance(r, torch.Tensor) and r.numel() == 1:
        return (8, "number")

    if isinstance(r, torch.Tensor):
        s = r.storage()
        nb = s.size() * s.element_size()
        if r.numel() < s.size():
            print(
                "Warning: the view of a larger tensor is stored, condider saving a clone to reduce size of the file"
            )
            return (nb, "tensor!")
        return (nb, "tensor")

    if isinstance(r, np.ndarray):
        return (r.size * r.itemsize, "np.array")

    if r is None:
        return (0, "none")

    if isinstance(r, str):
        return (len(r), "str")

    return (0, "unknown")


def to_kmg(x):
    if x > 1024**3:
        return "{:.1f}GiB".format(x / 1024**3)
    if x > 1024**2:
        return "{:.1f}MiB".format(x / 1024**2)
    if x > 1024:
        return "{:.1f}KiB".format(x / 1024)
    return "{}B".format(x)


def for_human(r):
    nb, x = r

    if isinstance(x, dict):
        d = {key: for_human(r) for key, r in x.items()}
        return (to_kmg(nb), d)

    if isinstance(x, list):
        c, o = x
        o = [for_human(r) for r in o]
        return (to_kmg(nb), [c, o])

    if isinstance(x, tuple):
        t = tuple(for_human(r) for r in x)
        return (to_kmg(nb), t)

    return x  # (to_kmg(nb), x)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("log_dir", type=str)
    parser.add_argument("--n", type=int)
    args = parser.parse_args()

    structures = []
    for i, r in enumerate(load_iter(args.log_dir)):
        r = get_structure(r)
        if r not in structures:
            structures.append(r)

        if args.n and i + 1 >= args.n:
            break

    print(
        "\n\n\n".join(
            json.dumps(for_human(s), indent=4, sort_keys=True) for s in structures
        )
    )


if __name__ == "__main__":
    main()
