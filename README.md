# GRID

## Install
```
python setup.py install
```

## Usage
The file `example.py` is a minimal script that can be used with `grid`.

```
python -m grid --log_dir results --cmd "python example.py" --a:int 1 2 3 --b:int 5 6 7
```
All the combination of (1, 2, 3) and (5, 6, 7) are executed in simultaneously
```
[a=1 b=5] python example.py --pickle results/09248.pkl --a 1 --b 5
[a=1 b=6] python example.py --pickle results/05269.pkl --a 1 --b 6
[a=1 b=7] python example.py --pickle results/06593.pkl --a 1 --b 7
[a=2 b=5] python example.py --pickle results/08496.pkl --a 2 --b 5
[a=2 b=6] python example.py --pickle results/02873.pkl --a 2 --b 6
[a=2 b=7] python example.py --pickle results/04742.pkl --a 2 --b 7
[a=3 b=5] python example.py --pickle results/07695.pkl --a 3 --b 5
[a=3 b=6] python example.py --pickle results/04901.pkl --a 3 --b 6
[a=3 b=7] python example.py --pickle results/00274.pkl --a 3 --b 7
```

```
python -m grid --log_dir results --cmd "python example.py" --a:int 1 2 3 --b:int 5 6 7 8
```
The results already done are not executed again
```
[a=1 b=5] already done
[a=1 b=6] already done
[a=1 b=7] already done
[a=1 b=8] python example.py --pickle results/05438.pkl --a 1 --b 8
[a=2 b=5] already done
[a=2 b=6] already done
[a=2 b=7] already done
[a=2 b=8] python example.py --pickle results/00786.pkl --a 2 --b 8
[a=3 b=5] already done
[a=3 b=6] already done
[a=3 b=7] already done
[a=3 b=8] python example.py --pickle results/05922.pkl --a 3 --b 8
```
