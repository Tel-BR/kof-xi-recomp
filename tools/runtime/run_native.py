#!/usr/bin/env python3
"""Launch the installed GPU runtime or a specifically selected diagnostic build."""

import argparse
from contextlib import ExitStack
import os
from pathlib import Path
import subprocess
import sys


REPO = Path(__file__).resolve().parents[2]
GPU_BUILD = REPO / "private/tools/PS2Recomp-Fixer/build/ps2recomp"
GPU_RUNNER = GPU_BUILD / "ps2xRuntime/Release/ps2EntryRunner.exe"


def from_repo(path):
    return (REPO / path).resolve()


def open_log(stack, name):
    if name is None:
        return None
    path = from_repo(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    return stack.enter_context(path.open("wb"))


def stop(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, help="explicit diagnostic executable")
    parser.add_argument("--replay", type=Path, help="power-on PCSX2 .p2m2 recording")
    parser.add_argument("--max-frames", type=int, help="stop at this emulated VSync")
    parser.add_argument("--timeout", type=float, help="stop after this many host seconds")
    parser.add_argument("--stdout", type=Path)
    parser.add_argument("--stderr", type=Path)
    parser.add_argument("--headless", action="store_true", help="legacy diagnostic executable only")
    parser.add_argument("--unthrottled", action="store_true", help="legacy diagnostic executable only")
    args = parser.parse_args(argv)
    if args.max_frames is not None and args.max_frames < 0:
        parser.error("--max-frames must be nonnegative")
    if args.timeout is not None and args.timeout < 0:
        parser.error("--timeout must be nonnegative")
    if (args.headless or args.unthrottled) and args.exe is None:
        parser.error("--headless and --unthrottled require an explicit legacy diagnostic --exe")

    exe = from_repo(args.exe) if args.exe else GPU_RUNNER
    if not exe.is_file():
        print(f"Runtime executable not found: {exe}\nBuild the GPU runtime with build_runtime.bat.", file=sys.stderr)
        return 1

    command = [str(exe)]
    env = dict(os.environ, KOF_VBLANK_WAKE1="1", KOF_GS_DISPFIX="1", DOD_FPS="1")
    cwd = exe.parent
    if args.headless or args.unthrottled:
        # Preserve explicit CPU diagnostic runs used by the historical speed measurements.
        cwd = REPO / "private"
        env.update(PS2X_CD_IMAGE=str(cwd / "ps2/PS2 - The King of Fighters XI.iso"),
                   PS2X_DISC_DIR=str(cwd / "extracted"))
        command.append(str(cwd / "extracted/SLUS_216.87"))
        if args.headless:
            command.append("--headless")
        if args.unthrottled:
            command.append("--unthrottled")
    if args.max_frames:
        command.extend(["--max-frames", str(args.max_frames)])
    if args.replay is not None:
        replay = from_repo(args.replay)
        if not replay.is_file():
            print(f"Replay file not found: {replay}", file=sys.stderr)
            return 1
        command.extend(["--replay", str(replay)])

    print(f"Launching {exe}", flush=True)
    if args.replay is not None:
        print(f"Replay {replay}", flush=True)
    with ExitStack() as stack:
        process = subprocess.Popen(command, cwd=cwd, env=env,
                                   stdout=open_log(stack, args.stdout), stderr=open_log(stack, args.stderr))
        try:
            return process.wait(timeout=args.timeout or None)
        except subprocess.TimeoutExpired:
            print(f"Stopped after {args.timeout:g} seconds.")
            return 124
        except KeyboardInterrupt:
            return 130
        finally:
            stop(process)


if __name__ == "__main__":
    sys.exit(main())
