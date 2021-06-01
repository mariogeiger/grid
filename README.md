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
[results/504721.pk a=1 b=5] python example.py --output results/504721.pk --a 1 --b 5
[results/956440.pk a=1 b=6] python example.py --output results/956440.pk --a 1 --b 6
[results/352305.pk a=1 b=7] python example.py --output results/352305.pk --a 1 --b 7
[results/839715.pk a=2 b=5] python example.py --output results/839715.pk --a 2 --b 5
[results/484878.pk a=2 b=6] python example.py --output results/484878.pk --a 2 --b 6
[results/598464.pk a=2 b=7] python example.py --output results/598464.pk --a 2 --b 7
[results/547794.pk a=3 b=5] python example.py --output results/547794.pk --a 3 --b 5
[results/451796.pk a=3 b=6] python example.py --output results/451796.pk --a 3 --b 6
[results/208445.pk a=3 b=7] python example.py --output results/208445.pk --a 3 --b 7
[results/504721.pk a=1 b=5] computation 1 / 3
[results/352305.pk a=1 b=7] computation 1 / 3
[results/956440.pk a=1 b=6] computation 1 / 3
[results/839715.pk a=2 b=5] computation 1 / 3
[results/484878.pk a=2 b=6] computation 1 / 3
[results/598464.pk a=2 b=7] computation 1 / 3
[results/547794.pk a=3 b=5] computation 1 / 3
[results/451796.pk a=3 b=6] computation 1 / 3
[results/208445.pk a=3 b=7] computation 1 / 3
[results/504721.pk a=1 b=5] computation 2 / 3
[results/352305.pk a=1 b=7] computation 2 / 3
[results/956440.pk a=1 b=6] computation 2 / 3
[results/839715.pk a=2 b=5] computation 2 / 3
[results/484878.pk a=2 b=6] computation 2 / 3
[results/598464.pk a=2 b=7] computation 2 / 3
[results/547794.pk a=3 b=5] computation 2 / 3
[results/451796.pk a=3 b=6] computation 2 / 3
[results/208445.pk a=3 b=7] computation 2 / 3
[results/504721.pk a=1 b=5] computation 3 / 3
[results/352305.pk a=1 b=7] computation 3 / 3
[results/956440.pk a=1 b=6] computation 3 / 3
[results/839715.pk a=2 b=5] computation 3 / 3
[results/504721.pk a=1 b=5] terminated
[results/352305.pk a=1 b=7] terminated
[results/956440.pk a=1 b=6] terminated
[results/839715.pk a=2 b=5] terminated
[results/484878.pk a=2 b=6] computation 3 / 3
[results/484878.pk a=2 b=6] terminated
[results/598464.pk a=2 b=7] computation 3 / 3
[results/598464.pk a=2 b=7] terminated
[results/547794.pk a=3 b=5] computation 3 / 3
[results/451796.pk a=3 b=6] computation 3 / 3
[results/208445.pk a=3 b=7] computation 3 / 3
[results/547794.pk a=3 b=5] terminated
[results/451796.pk a=3 b=6] terminated
[results/208445.pk a=3 b=7] terminated
```

```
python -m grid results "python example.py" --a 1 2 3 --b 5 6 7 8
```
The results already done are not executed again
```
[a=1 b=5] results/504721.pk
[a=1 b=6] results/956440.pk
[a=1 b=7] results/352305.pk
[results/984090.pk a=1 b=8] python example.py --output results/984090.pk --a 1 --b 8
[a=2 b=5] results/839715.pk
[a=2 b=6] results/484878.pk
[a=2 b=7] results/598464.pk
[results/462733.pk a=2 b=8] python example.py --output results/462733.pk --a 2 --b 8
[a=3 b=5] results/547794.pk
[a=3 b=6] results/451796.pk
[a=3 b=7] results/208445.pk
[results/176846.pk a=3 b=8] python example.py --output results/176846.pk --a 3 --b 8
[results/984090.pk a=1 b=8] computation 1 / 3
[results/462733.pk a=2 b=8] computation 1 / 3
[results/176846.pk a=3 b=8] computation 1 / 3
[results/984090.pk a=1 b=8] computation 2 / 3
[results/462733.pk a=2 b=8] computation 2 / 3
[results/176846.pk a=3 b=8] computation 2 / 3
[results/984090.pk a=1 b=8] computation 3 / 3
[results/462733.pk a=2 b=8] computation 3 / 3
[results/176846.pk a=3 b=8] computation 3 / 3
[results/462733.pk a=2 b=8] terminated
[results/984090.pk a=1 b=8] terminated
[results/176846.pk a=3 b=8] terminated
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

- `pyhton -m grid.clean log_dir` remove files with no content (typically resultant of interrupted runs)
- `pyhton -m grid.merge log_dir_src log_dir_dst`
- `pyhton -m grid.info log_dir`
