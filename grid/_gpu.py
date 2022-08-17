import glob
import os
import random
import subprocess


def check_pid(pid):
    """Check For the existence of a unix pid."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def get_free_gpus(maxLoad=0.5, maxMemory=0.5, maxProc=3):
    directory = os.path.join(os.environ["HOME"], ".grun")
    if not os.path.exists(directory):
        os.makedirs(directory)

    import GPUtil

    GPUs = GPUtil.getGPUs()

    GPUs = [gpu for gpu in GPUs if gpu.load < maxLoad and gpu.memoryUtil < maxMemory]

    running = [f.split("/")[-1].split("_") for f in glob.glob("/home/*/.grun/*")]
    running = [(int(pid), list(map(int, ids.split(",")))) for pid, ids in running]
    running = [(pid, ids) for pid, ids in running if check_pid(pid)]

    p = subprocess.Popen(["nvidia-smi"], stdout=subprocess.PIPE)
    out = p.stdout.read().decode("UTF-8").split("Processes:")[-1].split("\n")
    procs = [int(x.split()[1]) for x in out if "iB" in x]

    for gpu in GPUs:
        gpu.nproc = max(
            len([1 for pid, ids in running if gpu.id in ids]),
            len([1 for p in procs if p == gpu.id]),
        )

    GPUs = [gpu for gpu in GPUs if gpu.nproc < maxProc]
    random.shuffle(GPUs)
    GPUs = sorted(GPUs, key=lambda gpu: gpu.nproc)

    return GPUs
