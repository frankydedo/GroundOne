"""SoC power sampling with macOS powermetrics (needs the NOPASSWD sudoers rule for /usr/bin/powermetrics only).

`Meter` runs `sudo -n powermetrics --samplers cpu_power,gpu_power` in the background and keeps, per sample, the
elapsed time and the "Combined Power (CPU + GPU + ANE)". Energy = sum of power x elapsed. It covers the SoC compute
units only (no DRAM, display or SSD), which is what the thesis compares between systems on the same machine.
"""
import re
import subprocess
import threading

ELAPSED = re.compile(r"\(([\d.]+)ms elapsed\)")
COMBINED = re.compile(r"Combined Power \(CPU \+ GPU \+ ANE\): (\d+) mW")


class Meter:
    def __init__(self, interval_ms=200):
        self.interval_ms = interval_ms
        self.samples = []  # (elapsed ms, combined mW)

    def start(self):
        self.proc = subprocess.Popen(["sudo", "-n", "/usr/bin/powermetrics", "--samplers", "cpu_power,gpu_power",
                                      "-i", str(self.interval_ms)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                     text=True, bufsize=1)
        self.thread = threading.Thread(target=self._read, daemon=True)
        self.thread.start()
        return self

    def _read(self):
        elapsed = None
        for line in self.proc.stdout:
            m = ELAPSED.search(line)
            if m:
                elapsed = float(m.group(1))
                continue
            m = COMBINED.search(line)
            if m and elapsed is not None:
                self.samples.append((elapsed, float(m.group(1))))
                elapsed = None

    def stop(self):
        self.proc.terminate()  # sudo relays the signal to powermetrics
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.thread.join(timeout=5)
        return self.summary()

    def summary(self):
        t = sum(e for e, _ in self.samples) / 1000
        joules = sum(e * p for e, p in self.samples) / 1e6
        return {"samples": len(self.samples), "seconds": t, "joules": joules, "mean_watts": joules / t if t else None}
