import argparse
from grid import exec_list, load_iter
from tqdm.auto import tqdm


def main():
    parser = argparse.ArgumentParser("grid")
    parser.add_argument("log_dir_src", type=str, help="path to a directory")
    parser.add_argument("log_dir_dst", type=str, help="path to a directory")
    parser.add_argument("cmd", type=str, help="program to execute in parallel for the grid search")
    parser.add_argument("--n", type=int, help="maximum parallel instances (infinite by default)")
    parser.add_argument("--sleep", type=float, default=0, help="sleep time between two runs (in seconds)")
    args, argv = parser.parse_known_args()

    params = []
    for x in argv:
        assert x.startswith('--')
        params += [x[2:]]

    new_params = []

    for r in load_iter(args.log_dir_src, tqdm=tqdm):
        new_params += [
            [(p, r['args'][p]) for p in params]
        ]

    exec_list(args.log_dir_dst, args.cmd, new_params, args.sleep, args.n, tqdm)


if __name__ == '__main__':
    main()
