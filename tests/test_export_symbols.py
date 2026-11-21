#!/usr/bin/env python3
"""
Unit and integration tests for Ghidra function symbol export (Issue #3 / Task 2).
"""

import os
import csv
import tempfile
import unittest
from pathlib import Path

from tools.symbols.export_symbols import (
    SymbolExporter,
    EXPECTED_SLUS_SHA1,
    CODE_START_ADDR,
    CODE_END_ADDR,
    DATA_END_ADDR,
    TARGET_STALL_ADDR,
)


class TestExportSymbols(unittest.TestCase):

    def test_environment_verification_invalid_elf(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"NOT_A_VALID_ELF_BINARY")
            temp_elf = f.name
        try:
            exporter = SymbolExporter(elf_path=Path(temp_elf))
            with self.assertRaises(ValueError) as ctx:
                exporter.verify_environment()
            self.assertIn("ELF SHA-1 mismatch", str(ctx.exception))
        finally:
            if os.path.exists(temp_elf):
                os.remove(temp_elf)

    def test_environment_verification_missing_jdk(self):
        exporter = SymbolExporter(jdk_dir=Path("non_existent_jdk_path"))
        with self.assertRaises(FileNotFoundError) as ctx:
            exporter.verify_environment()
        self.assertIn("JDK java executable not found", str(ctx.exception))

    def test_environment_verification_missing_ghidra(self):
        real_jdk = Path("private/tools/jdk21")
        if not real_jdk.exists():
            self.skipTest("Real JDK not present in private/tools/jdk21")
        exporter = SymbolExporter(jdk_dir=real_jdk, ghidra_dir=Path("non_existent_ghidra_dir"))
        with self.assertRaises(FileNotFoundError) as ctx:
            exporter.verify_environment()
        self.assertIn("Ghidra analyzeHeadless not found", str(ctx.exception))

    def test_validation_rejects_missing_stall_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "symbols.csv"
            toml_path = Path(tmpdir) / "symbols.toml"

            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Start", "End", "Size"])
                writer.writerow(["entry_00100008", "0x00100008", "0x00100040", "56"])

            with open(toml_path, "w", encoding="utf-8") as f:
                f.write("[general]\nstubs = []\n")

            exporter = SymbolExporter(output_csv=csv_path, output_toml=toml_path)
            with self.assertRaises(ValueError) as ctx:
                exporter.validate_exported_symbols()
            self.assertIn("missing from exported symbols", str(ctx.exception))

    def test_validation_rejects_data_tail_pseudo_functions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "symbols.csv"
            toml_path = Path(tmpdir) / "symbols.toml"

            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Start", "End", "Size"])
                writer.writerow(["entry_00100008", "0x00100008", "0x00100040", "56"])
                # Stall target is present
                writer.writerow(["sub_001fb188", f"0x{TARGET_STALL_ADDR:08X}", f"0x{TARGET_STALL_ADDR+20:08X}", "20"])
                # But a pseudo-function in data tail is also present
                writer.writerow(["sub_00280830", f"0x{CODE_END_ADDR:08X}", "0x00280840", "16"])

            with open(toml_path, "w", encoding="utf-8") as f:
                f.write("[general]\nstubs = []\n")

            exporter = SymbolExporter(output_csv=csv_path, output_toml=toml_path)
            with self.assertRaises(ValueError) as ctx:
                exporter.validate_exported_symbols()
            self.assertIn("entries in data tail", str(ctx.exception))

    def test_real_exported_symbols_if_present(self):
        toml_path = Path("private/symbols.toml")
        csv_path = Path("private/symbols.csv")

        if not toml_path.exists() or not csv_path.exists():
            self.skipTest("Exported symbols not yet generated in private/")

        exporter = SymbolExporter(output_toml=toml_path, output_csv=csv_path)
        metrics = exporter.validate_exported_symbols()

        # 1. Total records must be comprehensive (> 20,000 including recovered symbols)
        self.assertGreater(metrics["total_records"], 20000)

        # 2. Target stall function 0x1FB188 must be present
        self.assertTrue(metrics["stall_target_present"])
        self.assertIn("1fb188", metrics["stall_target_name"].lower())

        # 3. Code bounds: minimum start >= 0x100008, maximum end <= 0x280830
        self.assertGreaterEqual(int(metrics["min_start"], 16), CODE_START_ADDR)
        self.assertLessEqual(int(metrics["max_end"], 16), CODE_END_ADDR)

        # 4. Zero data tail pseudo-functions
        self.assertEqual(metrics["data_tail_entries"], 0)

        # 5. Check CSV specific record for 0x1FB188
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = [r for r in reader if int(r[1], 16) == TARGET_STALL_ADDR]
            self.assertEqual(len(rows), 1, "Exactly one entry for 0x1FB188")
            stall_row = rows[0]
            self.assertEqual(int(stall_row[1], 16), TARGET_STALL_ADDR)
            self.assertEqual(int(stall_row[3]), 20, "Expected size 20 (5 instructions)")

        # 6. Check TOML contents
        with open(toml_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("[general]", content)
            self.assertIn("ghidra_output =", content)
            self.assertIn("stubs = [", content)
            self.assertIn("skip = []", content)
            self.assertIn("[ghidra_export]", content)


if __name__ == "__main__":
    unittest.main()
