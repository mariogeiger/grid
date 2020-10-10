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
[a=1 b=5] python example.py --output results/278358.zip --a 1 --b 5
[a=1 b=6] python example.py --output results/800881.zip --a 1 --b 6
[a=1 b=7] python example.py --output results/046793.zip --a 1 --b 7
[a=2 b=5] python example.py --output results/343585.zip --a 2 --b 5
[a=2 b=6] python example.py --output results/942793.zip --a 2 --b 6
[a=2 b=7] python example.py --output results/097749.zip --a 2 --b 7
[a=3 b=5] python example.py --output results/770557.zip --a 3 --b 5
[a=3 b=6] python example.py --output results/622183.zip --a 3 --b 6
[a=3 b=7] python example.py --output results/396400.zip --a 3 --b 7
[a=2 b=5] computation 1 / 3
[a=1 b=7] computation 1 / 3
[a=1 b=5] computation 1 / 3
[a=2 b=6] computation 1 / 3
[a=2 b=7] computation 1 / 3
[a=3 b=6] computation 1 / 3
[a=1 b=6] computation 1 / 3
[a=3 b=5] computation 1 / 3
[a=3 b=7] computation 1 / 3
[a=2 b=5] computation 2 / 3
[a=1 b=7] computation 2 / 3
[a=1 b=5] computation 2 / 3
[a=2 b=6] computation 2 / 3
[a=2 b=7] computation 2 / 3
[a=3 b=6] computation 2 / 3
[a=1 b=6] computation 2 / 3
[a=3 b=5] computation 2 / 3
[a=3 b=7] computation 2 / 3
[a=2 b=5] computation 3 / 3
[a=1 b=7] computation 3 / 3
[a=1 b=5] computation 3 / 3
[a=2 b=5] terminated
[a=2 b=6] computation 3 / 3
[a=2 b=7] computation 3 / 3
[a=3 b=6] computation 3 / 3
[a=1 b=6] computation 3 / 3
[a=3 b=5] computation 3 / 3
[a=3 b=7] computation 3 / 3
[a=1 b=7] terminated
[a=2 b=6] terminated
[a=1 b=5] terminated
[a=2 b=7] terminated
[a=3 b=6] terminated
[a=1 b=6] terminated
[a=3 b=5] terminated
[a=3 b=7] terminated
```

```
python -m grid results "python example.py" --a 1 2 3 --b 5 6 7 8
```
The results already done are not executed again
```
[a=1 b=5] results/278358.zip
[a=1 b=6] results/800881.zip
[a=1 b=7] results/046793.zip
[a=1 b=8] python example.py --output results/362135.zip --a 1 --b 8
[a=2 b=5] results/343585.zip
[a=2 b=6] results/942793.zip
[a=2 b=7] results/097749.zip
[a=2 b=8] python example.py --output results/731204.zip --a 2 --b 8
[a=3 b=5] results/770557.zip
[a=3 b=6] results/622183.zip
[a=3 b=7] results/396400.zip
[a=3 b=8] python example.py --output results/347413.zip --a 3 --b 8
[a=1 b=8] computation 1 / 3
[a=2 b=8] computation 1 / 3
[a=3 b=8] computation 1 / 3
[a=1 b=8] computation 2 / 3
[a=2 b=8] computation 2 / 3
[a=3 b=8] computation 2 / 3
[a=1 b=8] computation 3 / 3
[a=2 b=8] computation 3 / 3
[a=3 b=8] computation 3 / 3
[a=1 b=8] terminated
[a=2 b=8] terminated
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
