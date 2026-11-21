#!/usr/bin/env python3
"""
Integration and validation tests for Stage 3: Recompile ELF and Build Native Runtime (Issue #4).
Validates:
1. Exported symbols and recompilation inputs.
2. 0 unhandled instructions across the recompiled code.
3. Generation of native executable binary (PE64 x64).
4. Runtime execution progression past frame 439 (former 0x1FB188 stall).
"""

import os
import struct
import unittest
from pathlib import Path


TARGET_STALL_ADDR = 0x1FB188
MIN_EXECUTABLE_SIZE = 70 * 1024 * 1024  # 70 MB minimum for fully linked recompiled binary


class TestStage3Recompile(unittest.TestCase):

    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.toml_path = self.repo_root / "private" / "symbols.toml"
        self.csv_path = self.repo_root / "private" / "symbols.csv"
        self.native_exe = self.repo_root / "private" / "kof_xi_native.exe"
        self.runner_exe = self.repo_root / "private" / "tools" / "PS2Recomp" / "out" / "build" / "ps2xRuntime" / "ps2EntryRunner.exe"

    def test_symbols_configuration_integrity(self):
        """Verify symbols table includes target stall address and proper function count."""
        if not self.csv_path.exists():
            self.skipTest("private/symbols.csv not present in local test environment")

        with open(self.csv_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(f"0x{TARGET_STALL_ADDR:08X}", content, f"Stall target 0x{TARGET_STALL_ADDR:08X} missing from symbols.csv")
        self.assertIn("sub_001fb188", content, "sub_001fb188 missing from symbols.csv")

        line_count = len(content.strip().splitlines())
        self.assertGreater(line_count, 25000, f"Expected >25,000 symbols, got {line_count}")

    def test_native_executable_exists_and_valid_pe64(self):
        """Verify the compiled native executable is present and is a valid PE64 binary."""
        exe_path = self.native_exe if self.native_exe.exists() else self.runner_exe
        if not exe_path.exists():
            self.skipTest(f"Native binary not found at {self.native_exe} or {self.runner_exe}")

        size = exe_path.stat().st_size
        self.assertGreater(size, MIN_EXECUTABLE_SIZE, f"Binary size {size} bytes is smaller than expected minimum {MIN_EXECUTABLE_SIZE}")

        with open(exe_path, "rb") as f:
            header = f.read(2)
            self.assertEqual(header, b"MZ", "Executable missing DOS MZ header")
            f.seek(0x3C)
            pe_offset = struct.unpack("<I", f.read(4))[0]
            f.seek(pe_offset)
            pe_signature = f.read(4)
            self.assertEqual(pe_signature, b"PE\x00\x00", "Executable missing PE signature")
            machine = struct.unpack("<H", f.read(2))[0]
            self.assertEqual(machine, 0x8664, "Executable is not x86-64 (AMD64)")

    def test_no_unhandled_instructions_in_output(self):
        """Verify recompiled output contains zero UNHANDLED instruction comments."""
        output_dir = self.repo_root / "private" / "output"
        if not output_dir.exists():
            self.skipTest("private/output directory not present")

        # Fast scan across recompiled files for UNHANDLED markers
        unhandled_files = []
        for file in output_dir.glob("*.cpp"):
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "UNHANDLED" in line or "unhandled instruction" in line.lower():
                            unhandled_files.append((file.name, line.strip()))
                            break
            except Exception:
                continue

        self.assertEqual(len(unhandled_files), 0, f"Found unhandled instructions in {len(unhandled_files)} files: {unhandled_files[:5]}")

    def test_execution_advances_past_frame_439(self):
        """Verify native runtime execution log surpasses former frame 439 stall."""
        stdout_log = self.repo_root / "private" / "run_stdout.txt"
        if not stdout_log.exists():
            self.skipTest("private/run_stdout.txt not present")

        with open(stdout_log, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Check for tick progression well beyond 439 (e.g. tick 600+)
        has_post_439_tick = False
        max_vsync_tick = 0
        for line in content.splitlines():
            if "[run:tick]" in line and "tick=" in line:
                try:
                    parts = line.split("tick=")
                    tick_val = int(parts[1].split()[0])
                    if tick_val > 439:
                        has_post_439_tick = True
                except Exception:
                    pass
            if "[heartbeat]" in line and "vsyncTick=" in line:
                try:
                    parts = line.split("vsyncTick=")
                    vsync_val = int(parts[1].split()[0])
                    if vsync_val > max_vsync_tick:
                        max_vsync_tick = vsync_val
                except Exception:
                    pass

        self.assertTrue(has_post_439_tick, "Execution log did not advance past tick 439")
        self.assertGreater(max_vsync_tick, 439, f"Expected VSync tick > 439, got {max_vsync_tick}")
        self.assertIn("activeThreads=5", content, "Expected 5 active threads spawned in runtime")


if __name__ == "__main__":
    unittest.main()
