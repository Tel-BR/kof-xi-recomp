#!/usr/bin/env python3
"""
Verification Oracle and Test Harness with Replay Fidelity for KOF XI Recomp.

Validates simulation correctness and memory fidelity between the native port
and the PCSX2 reference emulator using .p2m2 replay injection and EE RAM checkpoints.

Per ADR-0004 and Ticket 21:
- Game EE RAM region: 0x00100000 to 0x01E2D480 (size: 30,594,176 bytes / ~29.17 MB).
- First 1 MB (< 0x00100000) is excluded to eliminate host OS / kernel noise.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple


GAME_RAM_START = 0x00100000
GAME_RAM_END = 0x01E2D480
GAME_RAM_SIZE = GAME_RAM_END - GAME_RAM_START  # 30,594,176 bytes
SCRATCHPAD_SIZE = 16 * 1024                    # 16,384 bytes


@dataclass
class OracleRunResult:
    returncode: int
    elapsed_seconds: float
    ram_dump_path: Optional[Path]
    ram_size: int
    ram_sha256: str
    stdout_lines: int
    stderr_lines: int


def extract_game_ram_from_full_ram(full_ram: bytes) -> bytes:
    """Extract game-owned EE RAM (0x100000..0x01E2D480) from a full 32 MB RDRAM image."""
    if len(full_ram) < GAME_RAM_END:
        raise ValueError(f"Full RAM buffer size {len(full_ram)} is smaller than GAME_RAM_END ({GAME_RAM_END})")
    return full_ram[GAME_RAM_START:GAME_RAM_END]


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 hexadecimal digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def extract_game_ram_from_p2s(p2s_path: Path) -> bytes:
    """Extract game-owned EE RAM from a PCSX2 .p2s savestate archive."""
    if not p2s_path.exists():
        raise FileNotFoundError(f"PCSX2 savestate not found: {p2s_path}")

    with zipfile.ZipFile(p2s_path, "r") as z:
        if "eeMemory.bin" not in z.namelist():
            raise KeyError(f"'eeMemory.bin' missing from savestate archive: {p2s_path}")
        ee_ram = z.read("eeMemory.bin")

    return extract_game_ram_from_full_ram(ee_ram)


def run_native_replay(
    exe_path: Path,
    elf_path: Path,
    iso_path: Path,
    replay_path: Path,
    max_frames: int = 1000,
    dump_ram_path: Optional[Path] = None,
    timeout: float = 60.0,
    unthrottled: bool = True,
    headless: bool = True,
    disc_dir: Optional[Path] = None,
) -> OracleRunResult:
    """
    Execute the native recompiled binary with .p2m2 replay input and capture EE RAM dump.
    """
    if not exe_path.exists():
        raise FileNotFoundError(f"Native binary not found: {exe_path}")
    if not elf_path.exists():
        raise FileNotFoundError(f"ELF binary not found: {elf_path}")
    if not iso_path.exists():
        raise FileNotFoundError(f"ISO image not found: {iso_path}")
    if not replay_path.exists():
        raise FileNotFoundError(f"Replay file not found: {replay_path}")

    repo_root = exe_path.resolve().parent.parent if exe_path.parent.name == "private" else exe_path.resolve().parent
    clang_bin = r"C:\Users\Admin\.local\share\retcomm\toolchains\cmake-clang-v1\latest\bin"

    env = os.environ.copy()
    env["PATH"] = f"{exe_path.parent};{clang_bin};{env.get('PATH', '')}"
    env["PS2X_DEFAULT_BOOT_ELF"] = str(elf_path.resolve())
    env["PS2X_CD_IMAGE"] = str(iso_path.resolve())
    if disc_dir and disc_dir.exists():
        env["PS2X_DISC_DIR"] = str(disc_dir.resolve())
    else:
        default_disc = repo_root / "private/extracted"
        if default_disc.exists():
            env["PS2X_DISC_DIR"] = str(default_disc.resolve())

    env["PS2X_HEADLESS"] = "1" if headless else "0"
    env["PS2X_UNTHROTTLED"] = "1" if unthrottled else "0"
    env["PS2X_MAX_FRAMES"] = str(max_frames)
    env["PS2X_REPLAY_P2M2"] = str(replay_path.resolve())

    temp_ram: Optional[Path] = None
    if dump_ram_path:
        dump_ram_path.parent.mkdir(parents=True, exist_ok=True)
        env["PS2X_DUMP_RAM"] = str(dump_ram_path.resolve())
    else:
        temp_ram = repo_root / "private" / f"temp_ram_{int(time.time()*1000)}.bin"
        env["PS2X_DUMP_RAM"] = str(temp_ram.resolve())

    cmd = [
        str(exe_path.resolve()),
        str(elf_path.resolve()),
        "--headless" if headless else "",
        "--unthrottled" if unthrottled else "",
        "--max-frames", str(max_frames),
        "--replay", str(replay_path.resolve()),
        "--dump-ram", str((dump_ram_path or temp_ram).resolve()),
    ]
    cmd = [c for c in cmd if c]

    start_time = time.time()
    proc = subprocess.Popen(
        cmd,
        env=env,
        cwd=str(exe_path.parent.resolve()),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        stdout_text, stderr_text = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout_text, stderr_text = proc.communicate()

    elapsed = time.time() - start_time
    target_ram = dump_ram_path or temp_ram

    ram_size = 0
    ram_hash = ""
    if target_ram and target_ram.exists():
        ram_bytes = target_ram.read_bytes()
        ram_size = len(ram_bytes)
        ram_hash = compute_sha256(ram_bytes)
        if temp_ram and temp_ram.exists() and not dump_ram_path:
            try:
                temp_ram.unlink()
            except OSError:
                pass

    return OracleRunResult(
        returncode=proc.returncode,
        elapsed_seconds=elapsed,
        ram_dump_path=dump_ram_path if dump_ram_path and dump_ram_path.exists() else None,
        ram_size=ram_size,
        ram_sha256=ram_hash,
        stdout_lines=len(stdout_text.splitlines()),
        stderr_lines=len(stderr_text.splitlines()),
    )


def compare_memory_regions(
    ram_a: bytes,
    ram_b: bytes,
    chunk_size: int = 4096,
) -> Dict[str, any]:
    """Compare two game-owned EE RAM buffers and report matching and diverging blocks."""
    if len(ram_a) != len(ram_b):
        raise ValueError(f"Buffers have different sizes: {len(ram_a)} vs {len(ram_b)}")

    total_chunks = len(ram_a) // chunk_size
    diff_chunks = []
    identical_chunks = 0

    for i in range(total_chunks):
        start = i * chunk_size
        end = start + chunk_size
        if ram_a[start:end] == ram_b[start:end]:
            identical_chunks += 1
        else:
            diff_chunks.append({
                "chunk_index": i,
                "vaddr_start": GAME_RAM_START + start,
                "vaddr_end": GAME_RAM_START + end,
            })

    similarity_pct = (identical_chunks / total_chunks) * 100.0 if total_chunks > 0 else 0.0

    return {
        "total_bytes": len(ram_a),
        "chunk_size": chunk_size,
        "total_chunks": total_chunks,
        "identical_chunks": identical_chunks,
        "differing_chunks_count": len(diff_chunks),
        "similarity_pct": similarity_pct,
        "sample_differing_chunks": diff_chunks[:10],
    }


def main():
    parser = argparse.ArgumentParser(description="KOF XI Verification Oracle and Replay Harness.")
    parser.add_argument("--exe", type=str, default="private/kof_xi_native.exe", help="Path to native executable")
    parser.add_argument("--elf", type=str, default="private/extracted/SLUS_216.87", help="Path to guest ELF")
    parser.add_argument("--iso", type=str, default="private/ps2/PS2 - The King of Fighters XI.iso", help="Path to ISO")
    parser.add_argument("--replay", type=str, default="private/tools/pcsx2/ticket19_trunc1000.p2m2", help="Path to .p2m2 replay")
    parser.add_argument("--max-frames", type=int, default=1000, help="Max frames to simulate")
    parser.add_argument("--dump-ram", type=str, default="private/ram_oracle_1000.bin", help="Path to output Game EE RAM dump")
    parser.add_argument("--timeout", type=float, default=60.0, help="Execution timeout in seconds")
    parser.add_argument("--p2s", type=str, help="Optional PCSX2 .p2s savestate to compare against")

    args = parser.parse_args()

    exe_path = Path(args.exe)
    elf_path = Path(args.elf)
    iso_path = Path(args.iso)
    replay_path = Path(args.replay)
    dump_path = Path(args.dump_ram) if args.dump_ram else None

    print(f"Running verification replay: {replay_path} ({args.max_frames} frames)...")
    result = run_native_replay(
        exe_path=exe_path,
        elf_path=elf_path,
        iso_path=iso_path,
        replay_path=replay_path,
        max_frames=args.max_frames,
        dump_ram_path=dump_path,
        timeout=args.timeout,
    )

    print(f"Run finished in {result.elapsed_seconds:.2f}s with exit code {result.returncode}")
    print(f"Game RAM Size: {result.ram_size} bytes (Expected: {GAME_RAM_SIZE})")
    print(f"Game RAM SHA-256: {result.ram_sha256}")

    if args.p2s:
        p2s_path = Path(args.p2s)
        print(f"\nComparing with PCSX2 reference state: {p2s_path}...")
        ref_ram = extract_game_ram_from_p2s(p2s_path)
        ref_sha256 = compute_sha256(ref_ram)
        print(f"Reference RAM SHA-256: {ref_sha256}")

        if dump_path and dump_path.exists():
            native_ram = dump_path.read_bytes()
            comparison = compare_memory_regions(native_ram, ref_ram)
            print(f"Memory similarity: {comparison['similarity_pct']:.2f}% ({comparison['identical_chunks']}/{comparison['total_chunks']} chunks match)")

    return 0 if result.returncode == 0 and result.ram_size == GAME_RAM_SIZE else 1


if __name__ == "__main__":
    sys.exit(main())
