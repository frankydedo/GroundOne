"""Run Phase 0 jobs one at a time under a memory guard.

Each job is a separate process. Every 2 s the guard checks system memory; if available memory drops
below MIN_AVAIL_GB, or swap in use grows by more than MAX_SWAP_GROWTH_GB since the job started, the job is
killed (whole process group) and the queue moves on. Every 60 s the top memory users are logged, so a
runaway process that is not ours can be identified afterwards.

Usage: python watchdog.py queue.txt   (one shell command per line, '#' comments allowed)
"""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import psutil

MIN_AVAIL_GB = float(os.environ.get("MIN_AVAIL_GB", 2.0))
MAX_SWAP_GROWTH_GB = float(os.environ.get("MAX_SWAP_GROWTH_GB", 3.0))
LOGS = Path(__file__).resolve().parents[1] / "logs"
LOGS.mkdir(exist_ok=True)
STATUS = LOGS / "watchdog.log"


def gb(x):
    return x / 1e9


def say(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(STATUS, "a") as f:
        f.write(line + "\n")


def top_procs(n=6):
    procs = []
    for p in psutil.process_iter(["name", "memory_info"]):
        try:
            procs.append((p.info["memory_info"].rss, p.info["name"], p.pid))
        except (psutil.Error, TypeError, AttributeError):
            pass
    procs.sort(reverse=True)
    return ", ".join(f"{name}({pid})={gb(rss):.1f}G" for rss, name, pid in procs[:n])


def tree_rss(proc):
    total = 0
    try:
        procs = [proc] + proc.children(recursive=True)
    except psutil.Error:
        return 0
    for p in procs:
        try:
            total += p.memory_info().rss
        except psutil.Error:
            pass
    return total


def run(cmd, idx):
    log_path = LOGS / f"job{idx:02d}.log"
    swap0 = psutil.swap_memory().used
    say(f"START job{idx:02d}: {cmd}  (avail {gb(psutil.virtual_memory().available):.1f} GB, swap {gb(swap0):.1f} GB)")
    with open(log_path, "w") as lf:
        proc = subprocess.Popen(cmd, shell=True, stdout=lf, stderr=subprocess.STDOUT,
                                cwd=Path(__file__).parent, start_new_session=True)
    ps = psutil.Process(proc.pid)
    t0 = time.time()
    reason = None
    try:
        reason = _monitor(proc, ps, swap0, idx, t0)
    finally:
        if proc.poll() is None:  # guard is exiting for any reason: never leave the job unsupervised
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
    dur = (time.time() - t0) / 60
    status = f"KILLED ({reason})" if reason else f"exit {proc.returncode}"
    say(f"END   job{idx:02d}: {status}, {dur:.1f} min, job peak RSS {gb(_peak['job']):.1f} GB, min avail {gb(_peak['avail']):.1f} GB")
    return reason is None and proc.returncode == 0


_peak = {}


def _monitor(proc, ps, swap0, idx, t0):
    peak_job, min_avail, last_top = 0, 1e12, 0
    reason = None
    while proc.poll() is None:
        vm = psutil.virtual_memory()
        swap_growth = psutil.swap_memory().used - swap0
        peak_job = max(peak_job, tree_rss(ps))
        min_avail = min(min_avail, vm.available)
        if gb(vm.available) < MIN_AVAIL_GB:
            reason = f"available memory {gb(vm.available):.2f} GB < {MIN_AVAIL_GB}"
        elif gb(swap_growth) > MAX_SWAP_GROWTH_GB:
            reason = f"swap grew by {gb(swap_growth):.2f} GB > {MAX_SWAP_GROWTH_GB}"
        if reason:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            break
        if time.time() - last_top > 60:
            try:
                top = top_procs()
            except Exception as e:  # noqa: BLE001  (never let monitoring kill the guard)
                top = f"unavailable ({e})"
            say(f"  job{idx:02d} {int(time.time()-t0)}s avail={gb(vm.available):.1f}G swap+={gb(swap_growth):.1f}G | top: {top}")
            last_top = time.time()
        time.sleep(2)
        _peak.update(job=peak_job, avail=min_avail)
    _peak.update(job=peak_job, avail=min_avail)
    return reason


if __name__ == "__main__":
    # The queue file is re-read after every job, so jobs can be appended while it runs.
    # A line 'END' stops the guard; otherwise it waits up to IDLE_MIN minutes for new jobs.
    idle_min = float(os.environ.get("IDLE_MIN", 30))
    say(f"guard started, MIN_AVAIL_GB={MIN_AVAIL_GB}, MAX_SWAP_GROWTH_GB={MAX_SWAP_GROWTH_GB}")
    i, idle_since = 0, time.time()
    while True:
        cmds = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
        if i < len(cmds):
            if cmds[i] == "END":
                break
            run(cmds[i], i)
            i, idle_since = i + 1, time.time()
        elif time.time() - idle_since > idle_min * 60:
            break
        else:
            time.sleep(10)
    say("queue finished")
