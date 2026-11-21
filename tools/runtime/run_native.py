#!/usr/bin/env python3
"""
Runner script for native port execution of KOF XI recomp.
Executes private/kof_xi_native.exe with the proper environment configuration.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run KOF XI native recompiled binary.")
    parser.add_argument("--timeout", type=float, default=15.0, help="Execution timeout in seconds (default: 15s, 0 for interactive)")
    parser.add_argument("--stdout", type=str, default="private/run_stdout.txt", help="Path to capture stdout")
    parser.add_argument("--stderr", type=str, default="private/run_stderr.txt", help="Path to capture stderr")
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

    clang_bin = r"C:\Users\Admin\.local\share\retcomm\toolchains\cmake-clang-v1\latest\bin"
    env = os.environ.copy()
    env["PATH"] = f"{repo_root / 'private'};{clang_bin};{env.get('PATH', '')}"
    env["PS2X_DEFAULT_BOOT_ELF"] = str(elf_path)
    env["PS2X_CD_IMAGE"] = str(iso_path)
    env["PS2X_DISC_DIR"] = str((repo_root / "private/extracted").resolve())

    stdout_path = Path(args.stdout) if Path(args.stdout).is_absolute() else repo_root / args.stdout
    stderr_path = Path(args.stderr) if Path(args.stderr).is_absolute() else repo_root / args.stderr
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)

    stdout_file = open(stdout_path, "w", encoding="utf-8", errors="replace")
    stderr_file = open(stderr_path, "w", encoding="utf-8", errors="replace")

    print(f"Executing native binary: {exe_path}")
    proc = subprocess.Popen(
        [str(exe_path), str(elf_path)],
        env=env,
        stdout=stdout_file,
        stderr=stderr_file,
        cwd=str((repo_root / "private").resolve()),
    )

    if args.timeout > 0:
        print(f"Running for {args.timeout}s...")
        try:
            time.sleep(args.timeout)
        except KeyboardInterrupt:
            pass
        finally:
            print("Terminating process...")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
                proc.wait()
    else:
        print("Running interactively (waiting for exit)...")
        proc.wait()

    stdout_file.close()
    stderr_file.close()
    print(f"Execution complete. Logs written to {stdout_path} and {stderr_path}")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
