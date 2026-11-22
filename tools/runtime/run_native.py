#!/usr/bin/env python3
"""
Runner script for native port execution of KOF XI recomp.
Executes private/kof_xi_native.exe with the proper environment configuration.

Supports:
- Interactive execution (default, stays open until window is closed)
- Replay playback (--replay <path_to_p2m2>)
- Headless execution (--headless)
- Unthrottled simulation (--unthrottled)
- Timed runs (--timeout <seconds>)
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run KOF XI native recompiled binary.")
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.0,
        help="Execution timeout in seconds (default: 0 for interactive / indefinite until window closed)",
    )
    parser.add_argument(
        "--replay",
        type=str,
        default=None,
        help="Path to .p2m2 replay file to play back (e.g. private/tools/pcsx2/ticket19_trunc1000.p2m2)",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=0,
        help="Maximum frames to execute before exiting (0 for unlimited)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without displaying a graphical window (useful for benchmarks/CI)",
    )
    parser.add_argument(
        "--unthrottled",
        action="store_true",
        help="Run unthrottled without 60 FPS frame pacing limit",
    )
    parser.add_argument(
        "--stdout",
        type=str,
        default=None,
        help="Path to capture stdout (default: printed directly to terminal)",
    )
    parser.add_argument(
        "--stderr",
        type=str,
        default=None,
        help="Path to capture stderr (default: printed directly to terminal)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    iso_path = (repo_root / "private/ps2/PS2 - The King of Fighters XI.iso").resolve()
    elf_path = (repo_root / "private/extracted/SLUS_216.87").resolve()
    exe_path = (repo_root / "private/kof_xi_native.exe").resolve()

    if not exe_path.exists():
        fallback_exe = repo_root / "private/tools/PS2Recomp/out/build/ps2xRuntime/ps2EntryRunner.exe"
        if fallback_exe.exists():
            exe_path = fallback_exe
        else:
            print(f"Error: Native binary not found at {exe_path}", file=sys.stderr)
            return 1

    if not elf_path.exists():
        print(f"Error: Game ELF not found at {elf_path}", file=sys.stderr)
        return 1

    if not iso_path.exists():
        print(f"Error: Game ISO not found at {iso_path}", file=sys.stderr)
        return 1

    clang_bin = r"C:\Users\Admin\.local\share\retcomm\toolchains\cmake-clang-v1\latest\bin"
    env = os.environ.copy()
    env["PATH"] = f"{repo_root / 'private'};{clang_bin};{env.get('PATH', '')}"
    env["PS2X_DEFAULT_BOOT_ELF"] = str(elf_path)
    env["PS2X_CD_IMAGE"] = str(iso_path)
    env["PS2X_DISC_DIR"] = str((repo_root / "private/extracted").resolve())

    cmd = [str(exe_path), str(elf_path)]

    if args.headless:
        env["PS2X_HEADLESS"] = "1"
        cmd.append("--headless")

    if args.unthrottled:
        env["PS2X_UNTHROTTLED"] = "1"
        cmd.append("--unthrottled")

    if args.max_frames > 0:
        env["PS2X_MAX_FRAMES"] = str(args.max_frames)
        cmd.extend(["--max-frames", str(args.max_frames)])

    if args.replay:
        replay_file = Path(args.replay)
        if not replay_file.is_absolute():
            replay_file = (repo_root / replay_file).resolve()
        if not replay_file.exists():
            print(f"Error: Replay file not found at {replay_file}", file=sys.stderr)
            return 1
        env["PS2X_REPLAY_P2M2"] = str(replay_file)
        cmd.extend(["--replay", str(replay_file)])
        print(f"Loading replay: {replay_file}")

    stdout_file = None
    stderr_file = None
    if args.stdout:
        out_p = Path(args.stdout) if Path(args.stdout).is_absolute() else repo_root / args.stdout
        out_p.parent.mkdir(parents=True, exist_ok=True)
        stdout_file = open(out_p, "w", encoding="utf-8", errors="replace")

    if args.stderr:
        err_p = Path(args.stderr) if Path(args.stderr).is_absolute() else repo_root / args.stderr
        err_p.parent.mkdir(parents=True, exist_ok=True)
        stderr_file = open(err_p, "w", encoding="utf-8", errors="replace")

    print(f"Executing native binary: {exe_path}")
    print(f"ELF: {elf_path}")
    print(f"ISO: {iso_path}")
    if args.timeout > 0:
        print(f"Running with {args.timeout}s timeout...")
    else:
        print("Running in interactive mode (close the game window or press Ctrl+C to stop)...")

    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=stdout_file or sys.stdout,
        stderr=stderr_file or sys.stderr,
        cwd=str((repo_root / "private").resolve()),
    )

    try:
        if args.timeout > 0:
            time.sleep(args.timeout)
            print(f"\nTimeout of {args.timeout}s reached. Terminating process...")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
                proc.wait()
        else:
            proc.wait()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Terminating process...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
            proc.wait()
    finally:
        if stdout_file:
            stdout_file.close()
        if stderr_file:
            stderr_file.close()

    print(f"Process exited with code {proc.returncode}")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
