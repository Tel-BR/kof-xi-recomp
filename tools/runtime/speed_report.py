#!/usr/bin/env python3
"""
Speed and audio report for a native runtime log (ticket 13 feedback loop).

Reads the stdout (and optionally stderr) captured from a headless run, for example:

    python tools/runtime/run_native.py --exe private/kof_xi_native.exe --headless --timeout 30 \
        --stdout private/scratch/run_out.txt --stderr private/scratch/run_err.txt
    python tools/runtime/speed_report.py private/scratch/run_out.txt private/scratch/run_err.txt

The runtime prints a `[heartbeat] vsyncTick=N threads=M` line about once per second.
The report gives the median number of emulated vsyncs per second once the game has
started its threads (real speed is 60) and counts CRI ADX output-setup failures in
stderr, a sign that no sound can be produced ("-" when no stderr file is given).

Capture output to files as above (direct file handles). Redirecting through a pipe
or PowerShell's Start-Process redirection made every log write block and cost about
30% of the measured speed.
"""

import argparse
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

GREEN_THRESHOLD = 57
GAME_THREADS = 5

_HEARTBEAT = re.compile(r"\[heartbeat\] vsyncTick=(\d+) threads=(\d+)")
_ADX_OUTPUT_FAILURE = "can't create PSM"


@dataclass(frozen=True)
class SpeedReport:
    in_game_seconds: int
    median_vsyncs_per_second: Optional[int]
    adx_output_failures: Optional[int]  # None when no stderr was given

    @property
    def verdict(self) -> str:
        if self.median_vsyncs_per_second is None:
            return "NO DATA"
        return "GREEN" if self.median_vsyncs_per_second >= GREEN_THRESHOLD else "RED"

    def format(self, tag: str) -> str:
        median = "-" if self.median_vsyncs_per_second is None else self.median_vsyncs_per_second
        failures = "-" if self.adx_output_failures is None else self.adx_output_failures
        return (
            f"[{tag}] in-game seconds={self.in_game_seconds} median vsyncs/s={median} "
            f"adx output failures={failures} verdict={self.verdict}"
        )


def summarize(stdout_text: str, stderr_text: Optional[str] = None, min_threads: int = GAME_THREADS) -> SpeedReport:
    beats = [(int(m.group(1)), int(m.group(2))) for m in _HEARTBEAT.finditer(stdout_text)]
    deltas = [
        tick - prev_tick
        for (prev_tick, prev_threads), (tick, threads) in zip(beats, beats[1:])
        if prev_threads >= min_threads and threads >= min_threads
    ]
    median = int(statistics.median_low(deltas)) if deltas else None
    failures = None if stderr_text is None else stderr_text.count(_ADX_OUTPUT_FAILURE)
    return SpeedReport(len(deltas), median, failures)


def _read(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    return Path(path).read_text(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Report emulated speed and audio signals from a runtime log.")
    parser.add_argument("stdout", help="Captured stdout of the run (holds the heartbeat lines)")
    parser.add_argument("stderr", nargs="?", default=None, help="Captured stderr of the run (optional)")
    parser.add_argument("--tag", default="run", help="Label printed at the start of the report line")
    parser.add_argument("--min-threads", type=int, default=GAME_THREADS,
                        help="Count only seconds where at least this many EE threads exist (default: %(default)s)")
    args = parser.parse_args()
    report = summarize(_read(args.stdout) or "", _read(args.stderr), args.min_threads)
    print(report.format(args.tag))
    return 0


if __name__ == "__main__":
    sys.exit(main())
