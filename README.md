# GRID

## Install
```
python setup.py install
```

## Usage
The file `example.py` is a minimal script that can be used with `grid`.

```
python -m grid results "python example.py" --a:int 1 2 3 --b:int 5 6 7
```
All the combination of (1, 2, 3) and (5, 6, 7) are executed in simultaneously
```
[a=1 b=5] python example.py --pickle results/03641.pkl --a 1 --b 5
[a=1 b=6] python example.py --pickle results/01614.pkl --a 1 --b 6
[a=1 b=7] python example.py --pickle results/09540.pkl --a 1 --b 7
[a=2 b=5] python example.py --pickle results/00760.pkl --a 2 --b 5
[a=2 b=6] python example.py --pickle results/09792.pkl --a 2 --b 6
[a=2 b=7] python example.py --pickle results/02423.pkl --a 2 --b 7
[a=3 b=5] python example.py --pickle results/08524.pkl --a 3 --b 5
[a=3 b=6] python example.py --pickle results/04318.pkl --a 3 --b 6
[a=3 b=7] python example.py --pickle results/01307.pkl --a 3 --b 7
[a=1 b=5] execute addition
[a=1 b=6] execute addition
[a=1 b=7] execute addition
[a=2 b=5] execute addition
[a=2 b=6] execute addition
[a=2 b=7] execute addition
[a=3 b=5] execute addition
[a=3 b=6] execute addition
[a=3 b=7] execute addition
[a=1 b=5] terminated with code 0
[a=1 b=6] terminated with code 0
[a=1 b=7] terminated with code 0
[a=2 b=5] terminated with code 0
[a=2 b=6] terminated with code 0
[a=2 b=7] terminated with code 0
[a=3 b=5] terminated with code 0
[a=3 b=6] terminated with code 0
[a=3 b=7] terminated with code 0
```

```
python -m grid results "python example.py" --a:int 1 2 3 --b:int 5 6 7 8
```
The results already done are not executed again
```
[a=1 b=5] already done
[a=1 b=6] already done
[a=1 b=7] already done
[a=1 b=8] python example.py --pickle results/00473.pkl --a 1 --b 8
[a=2 b=5] already done
[a=2 b=6] already done
[a=2 b=7] already done
[a=2 b=8] python example.py --pickle results/02906.pkl --a 2 --b 8
[a=3 b=5] already done
[a=3 b=6] already done
[a=3 b=7] already done
[a=3 b=8] python example.py --pickle results/04190.pkl --a 3 --b 8
[a=1 b=8] execute addition
[a=2 b=8] execute addition
[a=3 b=8] execute addition
[a=1 b=8] terminated with code 0
[a=2 b=8] terminated with code 0
[a=3 b=8] terminated with code 0
```

Example: using slurm and only varying parameter b
```
python -m grid results "srun --partition gpu --qos gpu --gres gpu:1 --time 3-00:00:00 --mem 12G --pty python example.py --a 4" --b:int 5 6 7
```
