# pylint: disable=C
import argparse
import json

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
        return {key: get_structure(val) for key, val in r.items()}

    if isinstance(r, list):
        out = []
        for x in r:
            x = get_structure(x)
            if x not in out:
                out.append(x)
        return list(out)

    if isinstance(r, tuple):
        return tuple(get_structure(x) for x in r)

    return 'data'


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

    print('\n\n\n'.join(json.dumps(s, indent=4, sort_keys=True) for s in structures))


if __name__ == '__main__':
    main()
