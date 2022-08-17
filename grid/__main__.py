import argparse
from grid import exec_grid
from tqdm.auto import tqdm


def main():
    parser = argparse.ArgumentParser("grid")
    parser.add_argument("log_dir", type=str, help="path to a directory")
    parser.add_argument("cmd", type=str, help="program to execute in parallel for the grid search")
    parser.add_argument("--n", type=int, help="maximum parallel instances (infinite by default)")
    parser.add_argument(
        "--sleep",
        type=float,
        default=0,
        help="sleep time between two runs (in seconds)",
    )
    args, argv = parser.parse_known_args()

    params = []
    for x in argv:
        if x.startswith("--"):
            if ":" in x:
                name, typ = x[2:].split(":")
                typ = eval(typ)
            else:
                name = x[2:]
                typ = None
            params.append((name, typ, [], set()))
        else:
            name, typ, vals, opt = params[-1]
            if x in ["-r"]:
                opt.add(x)
            elif ":" in x:
                start, end = x.split(":")
                for i in range(int(start), int(end)):
                    vals.append(i)
            else:
                if typ is None:
                    x = eval(x)
                    if isinstance(x, list):
                        vals += x
                    else:
                        vals.append(x)
                else:
                    vals.append(typ(x))

    assert all([opt == set() or opt == {"-r"} for name, typ, vals, opt in params])
    params = [(name, reversed(vals) if "-r" in opt else vals) for name, typ, vals, opt in params]

    exec_grid(args.log_dir, args.cmd, params, args.sleep, args.n, tqdm)


if __name__ == "__main__":
    main()
