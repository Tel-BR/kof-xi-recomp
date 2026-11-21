#!/usr/bin/env python3
"""
Unit and integration tests for Seam 2: Verification Oracle Test Harness with Replay Fidelity (Issue #5 / Task 4).

Validates:
1. P2M2 replay format parsing (header, DualShock 2 controller packets, frame counts).
2. Integrity of recorded reference replays (ticket19.p2m2 and ticket19_trunc1000.p2m2).
3. EE Game RAM boundary extraction per ADR-0004 (0x100000 to 0x01E2D480).
4. PCSX2 .p2s savestate archive extraction and memory slicing.
5. Deterministic replay execution fidelity on the native recompiled binary.
"""

import hashlib
import os
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.oracle.p2m2_parser import (
    HEADER_SIZE,
    FRAME_PAYLOAD_SIZE,
    P2M2Replay,
    P2M2Header,
    DS2ControllerState,
    P2M2Frame,
)
from tools.oracle.verification_oracle import (
    GAME_RAM_START,
    GAME_RAM_END,
    GAME_RAM_SIZE,
    extract_game_ram_from_full_ram,
    extract_game_ram_from_p2s,
    compute_sha256,
    compare_memory_regions,
    run_native_replay,
)


class TestVerificationOracle(unittest.TestCase):

    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.replay_full = self.repo_root / "private/tools/pcsx2/ticket19.p2m2"
        self.replay_trunc = self.repo_root / "private/tools/pcsx2/ticket19_trunc1000.p2m2"
        self.p2s_ref = self.repo_root / "private/tools/pcsx2/sstates/SLUS-21687 (581A4DAA).01.p2s"
        self.native_exe = self.repo_root / "private/kof_xi_native.exe"
        self.elf_path = self.repo_root / "private/extracted/SLUS_216.87"
        self.iso_path = self.repo_root / "private/ps2/PS2 - The King of Fighters XI.iso"

    def test_p2m2_parser_synthetic_replay(self):
        """Test parsing of a synthetic .p2m2 buffer with known button inputs."""
        header = bytearray(HEADER_SIZE)
        header[0] = 0x01  # format version
        tag = b"PCSX2-v2.8.2\x00"
        header[1 : 1 + len(tag)] = tag
        author = b"Tester\x00"
        header[51 : 51 + len(author)] = author
        title = b"TestGame\x00"
        header[306 : 306 + len(title)] = title
        struct.pack_into("<I", header, 561, 2)  # total_frames = 2

        # Frame 0: Port 0 presses CROSS (bit 14 = 0 in active-low uint16 mask)
        p0_f0_buttons = 0xFFFF & ~(1 << 14)
        p0_f0 = struct.pack("<H4B12B", p0_f0_buttons, 128, 128, 128, 128, *([0] * 12))
        p1_f0 = struct.pack("<H4B12B", 0xFFFF, 128, 128, 128, 128, *([0] * 12))

        # Frame 1: Port 0 presses START (bit 3 = 0)
        p0_f1_buttons = 0xFFFF & ~(1 << 3)
        p0_f1 = struct.pack("<H4B12B", p0_f1_buttons, 128, 128, 128, 128, *([0] * 12))
        p1_f1 = struct.pack("<H4B12B", 0xFFFF, 128, 128, 128, 128, *([0] * 12))

        data = bytes(header) + p0_f0 + p1_f0 + p0_f1 + p1_f1

        # Test loading directly from bytes
        replay_bytes = P2M2Replay.load(data)
        self.assertEqual(replay_bytes.total_frames, 2)
        self.assertEqual(replay_bytes.header.author, "Tester")
        self.assertEqual(replay_bytes.header.game_title, "TestGame")

        f0 = replay_bytes.get_frame(0)
        self.assertTrue(f0.port0.is_button_pressed(1 << 14))
        self.assertIn("CROSS", f0.port0.pressed_button_names)

        f1 = replay_bytes.get_frame(1)
        self.assertTrue(f1.port0.is_button_pressed(1 << 3))
        self.assertIn("START", f1.port0.pressed_button_names)

        # Test loading from disk file (ensuring handle closed before read)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".p2m2") as f:
            f.write(data)
            temp_path = Path(f.name)

        try:
            replay_file = P2M2Replay.load(temp_path)
            self.assertEqual(replay_file.total_frames, 2)
            self.assertEqual(replay_file.header.author, "Tester")
            self.assertTrue(replay_file.get_frame(0).port0.is_button_pressed(1 << 14))
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_reference_replay_files_integrity(self):
        """Verify ticket19.p2m2 and ticket19_trunc1000.p2m2 structure and frame counts."""
        if not self.replay_trunc.exists():
            self.skipTest("private/tools/pcsx2/ticket19_trunc1000.p2m2 not found in workspace")

        replay_trunc = P2M2Replay.load(self.replay_trunc)
        self.assertEqual(replay_trunc.total_frames, 1000)
        self.assertEqual(self.replay_trunc.stat().st_size, HEADER_SIZE + 1000 * FRAME_PAYLOAD_SIZE)

        if self.replay_full.exists():
            replay_full = P2M2Replay.load(self.replay_full)
            self.assertEqual(replay_full.total_frames, 11782)
            self.assertEqual(self.replay_full.stat().st_size, HEADER_SIZE + 11782 * FRAME_PAYLOAD_SIZE)

    def test_game_ram_boundary_sizes(self):
        """Validate ADR-0004 Game EE RAM boundaries (0x100000..0x01E2D480)."""
        self.assertEqual(GAME_RAM_START, 0x00100000)
        self.assertEqual(GAME_RAM_END, 0x01E2D480)
        self.assertEqual(GAME_RAM_SIZE, 30594176)

        # Full 32 MB synthetic RAM
        full_ram = bytearray(32 * 1024 * 1024)
        full_ram[0x00100000] = 0xAA
        full_ram[0x01E2D47F] = 0xBB

        game_ram = extract_game_ram_from_full_ram(full_ram)
        self.assertEqual(len(game_ram), GAME_RAM_SIZE)
        self.assertEqual(game_ram[0], 0xAA)
        self.assertEqual(game_ram[-1], 0xBB)

    def test_p2s_savestate_extraction(self):
        """Test extraction of Game EE RAM from PCSX2 .p2s zip archive."""
        full_ram = bytearray(32 * 1024 * 1024)
        full_ram[0x00100000] = 0x42

        with tempfile.NamedTemporaryFile(delete=False, suffix=".p2s") as f:
            temp_p2s = Path(f.name)

        try:
            with zipfile.ZipFile(temp_p2s, "w") as z:
                z.writestr("eeMemory.bin", bytes(full_ram))

            extracted = extract_game_ram_from_p2s(temp_p2s)
            self.assertEqual(len(extracted), GAME_RAM_SIZE)
            self.assertEqual(extracted[0], 0x42)
        finally:
            if temp_p2s.exists():
                temp_p2s.unlink()

    def test_memory_region_comparison(self):
        """Test compare_memory_regions chunk comparison helper."""
        buf_a = bytearray(GAME_RAM_SIZE)
        buf_b = bytearray(GAME_RAM_SIZE)

        # Identical
        cmp_ident = compare_memory_regions(buf_a, buf_b)
        self.assertEqual(cmp_ident["similarity_pct"], 100.0)
        self.assertEqual(cmp_ident["differing_chunks_count"], 0)

        # Modify one chunk
        buf_b[5000] = 0xFF
        cmp_diff = compare_memory_regions(buf_a, buf_b, chunk_size=4096)
        self.assertLess(cmp_diff["similarity_pct"], 100.0)
        self.assertEqual(cmp_diff["differing_chunks_count"], 1)

    def test_native_replay_deterministic_execution(self):
        """Execute a short replay run (100 frames) and verify deterministic RAM state."""
        if not self.native_exe.exists() or not self.elf_path.exists() or not self.iso_path.exists():
            self.skipTest("Game binaries / ISO not found in private/")
        if not self.replay_trunc.exists():
            self.skipTest("Replay file not found in private/tools/pcsx2/")

        with tempfile.TemporaryDirectory() as tmpdir:
            dump_a = Path(tmpdir) / "ram_a.bin"
            dump_b = Path(tmpdir) / "ram_b.bin"

            res_a = run_native_replay(
                exe_path=self.native_exe,
                elf_path=self.elf_path,
                iso_path=self.iso_path,
                replay_path=self.replay_trunc,
                max_frames=100,
                dump_ram_path=dump_a,
                timeout=20.0,
                unthrottled=True,
                headless=True,
            )

            self.assertEqual(res_a.returncode, 0, f"Native run failed with returncode {res_a.returncode}")
            self.assertEqual(res_a.ram_size, GAME_RAM_SIZE, f"Expected {GAME_RAM_SIZE} bytes, got {res_a.ram_size}")
            self.assertTrue(dump_a.exists())

            # Second identical run to verify 100% determinism
            res_b = run_native_replay(
                exe_path=self.native_exe,
                elf_path=self.elf_path,
                iso_path=self.iso_path,
                replay_path=self.replay_trunc,
                max_frames=100,
                dump_ram_path=dump_b,
                timeout=20.0,
                unthrottled=True,
                headless=True,
            )

            self.assertEqual(res_b.returncode, 0)
            self.assertEqual(res_a.ram_sha256, res_b.ram_sha256, "Memory state diverged between two identical runs!")


if __name__ == "__main__":
    unittest.main()
