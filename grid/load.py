# pylint: disable=missing-docstring, bare-except
import glob
import os

import torch


def load(directory, verbose=False):
    runs = []
    for file in sorted(glob.glob(os.path.join(directory, '*.pkl'))):
        if verbose:
            print(file)
        with open(file, 'rb') as file:
            try:
                torch.load(file)
                run = torch.load(file, map_location='cpu')
            except:
                continue
        runs.append(run)
    return runs
