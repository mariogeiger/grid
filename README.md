# GRID

## Install
```
pip install git+https://github.com/mariogeiger/grid
```
or in local
```
python setup.py install
```

## Usage
### Save results
The file `example.py` is a minimal script that can be used with `grid`.

```
python -m grid results "python example.py" --a 1 2 3 --b 5 6 7
```
All the combination of (1, 2, 3) and (5, 6, 7) are executed in simultaneously
```
[a=1 b=5] python example.py --output results/502680.pk --a 1 --b 5
[a=1 b=6] python example.py --output results/891421.pk --a 1 --b 6
[a=1 b=7] python example.py --output results/107761.pk --a 1 --b 7
[a=2 b=5] python example.py --output results/494144.pk --a 2 --b 5
[a=2 b=6] python example.py --output results/687939.pk --a 2 --b 6
[a=2 b=7] python example.py --output results/329136.pk --a 2 --b 7
[a=3 b=5] python example.py --output results/502988.pk --a 3 --b 5
[a=3 b=6] python example.py --output results/488419.pk --a 3 --b 6
[a=3 b=7] python example.py --output results/863147.pk --a 3 --b 7
[a=1 b=5] computation 1 / 3
[a=1 b=6] computation 1 / 3
[a=1 b=7] computation 1 / 3
[a=2 b=5] computation 1 / 3
[a=2 b=6] computation 1 / 3
[a=2 b=7] computation 1 / 3
[a=3 b=5] computation 1 / 3
[a=3 b=6] computation 1 / 3
[a=3 b=7] computation 1 / 3
[a=1 b=5] computation 2 / 3
[a=1 b=6] computation 2 / 3
[a=1 b=7] computation 2 / 3
[a=2 b=5] computation 2 / 3
[a=2 b=6] computation 2 / 3
[a=2 b=7] computation 2 / 3
[a=3 b=5] computation 2 / 3
[a=3 b=6] computation 2 / 3
[a=3 b=7] computation 2 / 3
[a=1 b=5] computation 3 / 3
[a=1 b=6] computation 3 / 3
[a=1 b=7] computation 3 / 3
[a=2 b=5] computation 3 / 3
[a=1 b=6] terminated
[a=1 b=5] terminated
[a=2 b=6] computation 3 / 3
[a=1 b=7] terminated
[a=2 b=5] terminated
[a=2 b=6] terminated
[a=2 b=7] computation 3 / 3
[a=2 b=7] terminated
[a=3 b=5] computation 3 / 3
[a=3 b=5] terminated
[a=3 b=6] computation 3 / 3
[a=3 b=7] computation 3 / 3
[a=3 b=6] terminated
[a=3 b=7] terminated
```

```
python -m grid results "python example.py" --a 1 2 3 --b 5 6 7 8
```
The results already done are not executed again
```
[a=1 b=5] results/502680.pk
[a=1 b=6] results/891421.pk
[a=1 b=7] results/107761.pk
[a=1 b=8] python example.py --output results/979829.pk --a 1 --b 8
[a=2 b=5] results/494144.pk
[a=2 b=6] results/687939.pk
[a=2 b=7] results/329136.pk
[a=2 b=8] python example.py --output results/951081.pk --a 2 --b 8
[a=3 b=5] results/502988.pk
[a=3 b=6] results/488419.pk
[a=3 b=7] results/863147.pk
[a=3 b=8] python example.py --output results/607822.pk --a 3 --b 8
[a=2 b=8] computation 1 / 3
[a=1 b=8] computation 1 / 3
[a=3 b=8] computation 1 / 3
[a=2 b=8] computation 2 / 3
[a=1 b=8] computation 2 / 3
[a=3 b=8] computation 2 / 3
[a=2 b=8] computation 3 / 3
[a=2 b=8] terminated
[a=1 b=8] computation 3 / 3
[a=3 b=8] computation 3 / 3
[a=1 b=8] terminated
[a=3 b=8] terminated
```

Example: using slurm and only varying parameter b
```
python -m grid results "srun --partition gpu --qos gpu --gres gpu:1 --time 3-00:00:00 --mem 12G --pty python example.py --a 4" --b:int 5 6 7
```

### Load results
```python
from grid import load

runs = load('./results/')
print('{} results loaded'.format(len(runs)))
```

### Load in groups
```python
from grid import load_grouped
import matplotlib.pyplot as plt

args, groups = load_grouped('./results/', ['b'])

for param, rs in groups:
    rs = sorted(rs, key=lambda r: r['args'].b)
    label = "a={0[a]}".format(param)
    plt.plot([r['args'].b for r in rs], [r['division'] for r in rs], label=label)
```

## Optional arguments

`--n N` maximum number of job running in the same time

`--sleep S` time to sleep in seconds between two job launch

## Subcommands

- `pyhton -m grid.clear log_dir` remove files with no content (typically resultant of interrupted runs)
- `pyhton -m grid.merge log_dir_src log_dir_dst`
- `pyhton -m grid.info log_dir`
