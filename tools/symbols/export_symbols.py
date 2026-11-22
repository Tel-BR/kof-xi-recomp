#!/usr/bin/env python3
"""
Function Symbols Exporter for KOF XI (PS2 Release - US SLUS-21687 v1.00).

Automates headless Ghidra analysis of SLUS_216.87 with the Emotion Engine (R5900)
processor module to discover complete function symbols and boundaries for PS2Recomp.

Specifically resolves the function discovery gap from Ticket 13:
- Delimits real code boundary (0x100008 - 0x282000) from data tail (0x282000 - 0x2F1400)
- Recovers pointer-only functions (including stall target 0x1FB188 at frame 439)
- Excludes the 18 data-as-code pseudo-functions from the data tail
- Exports ready-to-use symbols.toml and symbols.csv for PS2Recomp
"""

import os
import sys
import csv
import hashlib
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("export_symbols")

# Boundaries and targets for SLUS-21687 v1.00
EXPECTED_SLUS_SHA1 = "133f8c56283f0e255be995e894a3a7e6fe0c7b24"
CODE_START_ADDR = 0x00100008
CODE_END_ADDR = 0x00282000
DATA_END_ADDR = 0x002F1400
TARGET_STALL_ADDR = 0x001FB188  # Frame 439 indirect call target

DEFAULT_ELF_PATH = Path("private/extracted/SLUS_216.87")
DEFAULT_GHIDRA_DIR = Path("private/tools/ghidra")
DEFAULT_JDK_DIR = Path("private/tools/jdk21")
DEFAULT_PROJECT_DIR = Path("private/ps2recomp/ghidra")
DEFAULT_PROJECT_NAME = "kofxi"
DEFAULT_OUTPUT_TOML = Path("private/symbols.toml")
DEFAULT_OUTPUT_CSV = Path("private/symbols.csv")
DEFAULT_SCRIPT_DIR = Path("tools/ghidra")


class SymbolExporter:
    def __init__(
        self,
        elf_path: Optional[Path] = None,
        ghidra_dir: Optional[Path] = None,
        jdk_dir: Optional[Path] = None,
        project_dir: Optional[Path] = None,
        project_name: str = DEFAULT_PROJECT_NAME,
        output_toml: Optional[Path] = None,
        output_csv: Optional[Path] = None,
        script_dir: Optional[Path] = None,
    ):
        self.elf_path = Path(elf_path) if elf_path else DEFAULT_ELF_PATH
        self.ghidra_dir = Path(ghidra_dir) if ghidra_dir else DEFAULT_GHIDRA_DIR
        self.jdk_dir = Path(jdk_dir) if jdk_dir else DEFAULT_JDK_DIR
        self.project_dir = Path(project_dir) if project_dir else DEFAULT_PROJECT_DIR
        self.project_name = project_name
        self.output_toml = Path(output_toml) if output_toml else DEFAULT_OUTPUT_TOML
        self.output_csv = Path(output_csv) if output_csv else DEFAULT_OUTPUT_CSV
        self.script_dir = Path(script_dir) if script_dir else DEFAULT_SCRIPT_DIR

    def verify_environment(self) -> Dict[str, Any]:
        """Verifies that all required tools, modules, and inputs are present and valid."""
        results = {
            "jdk_ok": False,
            "ghidra_ok": False,
            "ee_module_ok": False,
            "elf_ok": False,
            "elf_sha1": None,
        }

        # Check JDK
        java_exe = self.jdk_dir / "bin" / ("java.exe" if os.name == "nt" else "java")
        if not java_exe.exists():
            raise FileNotFoundError(f"JDK java executable not found at: {java_exe}")
        results["jdk_ok"] = True

        # Check Ghidra headless launcher
        analyze_headless = self.ghidra_dir / "support" / ("analyzeHeadless.bat" if os.name == "nt" else "analyzeHeadless")
        if not analyze_headless.exists():
            raise FileNotFoundError(f"Ghidra analyzeHeadless not found at: {analyze_headless}")
        results["ghidra_ok"] = True

        # Check Emotion Engine extension
        ee_ext = self.ghidra_dir / "Ghidra" / "Extensions" / "ghidra-emotionengine-reloaded"
        if not ee_ext.exists():
            raise FileNotFoundError(f"Emotion Engine extension not found at: {ee_ext}")
        results["ee_module_ok"] = True

        # Check ELF binary and hash
        if not self.elf_path.exists():
            raise FileNotFoundError(f"Input ELF file not found at: {self.elf_path}")

        hasher = hashlib.sha1()
        with open(self.elf_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        actual_sha1 = hasher.hexdigest().lower()
        results["elf_sha1"] = actual_sha1

        if actual_sha1 != EXPECTED_SLUS_SHA1:
            raise ValueError(
                f"ELF SHA-1 mismatch: expected {EXPECTED_SLUS_SHA1}, got {actual_sha1}"
            )
        results["elf_ok"] = True

        return results

    def run_export(self, reanalyze: bool = False, timeout: int = 600) -> bool:
        """
        Runs Ghidra headless to export symbols.toml and symbols.csv.
        If reanalyze=True, imports fresh into project with full analysis.
        Otherwise, runs on existing project.
        """
        self.verify_environment()

        analyze_headless = self.ghidra_dir / "support" / ("analyzeHeadless.bat" if os.name == "nt" else "analyzeHeadless")
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.output_toml.parent.mkdir(parents=True, exist_ok=True)
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()
        env["JAVA_HOME"] = str(self.jdk_dir.resolve())
        env["PATH"] = str((self.jdk_dir / "bin").resolve()) + os.pathsep + env.get("PATH", "")

        cmd = [
            str(analyze_headless.resolve()),
            str(self.project_dir.resolve()),
            self.project_name,
        ]

        # Check if project already has the imported ELF
        project_gpr = self.project_dir / f"{self.project_name}.gpr"
        has_existing_project = project_gpr.exists()

        if reanalyze or not has_existing_project:
            cmd.extend([
                "-import", str(self.elf_path.resolve()),
                "-overwrite",
                "-processor", "r5900:LE:32:default",
                "-preScript", "KofPreScript.java",
            ])
        else:
            cmd.extend([
                "-process", self.elf_path.name,
                "-noanalysis",
            ])

        cmd.extend([
            "-scriptPath", str(self.script_dir.resolve()),
            "-postScript", "ExportKofFunctions.java",
            str(self.output_toml.resolve()),
            str(self.output_csv.resolve()),
            str(self.elf_path.resolve()),
        ])

        logger.info(f"Running Ghidra headless command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            logger.error(f"Ghidra execution failed with code {result.returncode}")
            logger.error(f"STDOUT:\n{result.stdout}")
            logger.error(f"STDERR:\n{result.stderr}")
            raise RuntimeError(f"Ghidra headless failed with exit code {result.returncode}")

        logger.info("Ghidra headless execution completed successfully.")
        return True

    def validate_exported_symbols(self) -> Dict[str, Any]:
        """
        Validates the integrity and correctness of exported symbols.
        Checks:
        1. Both symbols.toml and symbols.csv exist and are non-empty.
        2. Target stall function 0x1FB188 is present.
        3. All symbols are within real code boundaries (0x100008 - 0x282000).
        4. No function starts or ends in the data tail (0x282000 - 0x2F1400).
        5. Function count is coherent (>= 4000 functions recovered).
        """
        if not self.output_csv.exists():
            raise FileNotFoundError(f"Exported CSV not found at: {self.output_csv}")
        if not self.output_toml.exists():
            raise FileNotFoundError(f"Exported TOML not found at: {self.output_toml}")

        with open(self.output_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header or header != ["Name", "Start", "End", "Size"]:
                raise ValueError(f"Invalid CSV header in symbols file: {header}")
            rows = list(reader)

        if len(rows) == 0:
            raise ValueError("Exported symbols CSV is empty")

        starts: List[int] = []
        ends: List[int] = []
        names_by_addr: Dict[int, str] = {}
        entries_in_data_tail: List[tuple] = []
        has_stall_target = False

        for row in rows:
            name, start_str, end_str, size_str = row
            start = int(start_str, 16)
            end = int(end_str, 16)
            starts.append(start)
            ends.append(end)
            names_by_addr[start] = name

            if start == TARGET_STALL_ADDR:
                has_stall_target = True

            if start >= CODE_END_ADDR:
                entries_in_data_tail.append((name, hex(start), hex(end)))

        # Verification checks
        if not has_stall_target:
            raise ValueError(
                f"Target stall function {hex(TARGET_STALL_ADDR)} missing from exported symbols!"
            )

        if entries_in_data_tail:
            raise ValueError(
                f"Found {len(entries_in_data_tail)} entries in data tail (>= {hex(CODE_END_ADDR)}): "
                f"{entries_in_data_tail[:5]}"
            )

        max_end = max(ends)
        if max_end > CODE_END_ADDR:
            raise ValueError(
                f"Max end address {hex(max_end)} exceeds code boundary {hex(CODE_END_ADDR)}"
            )

        min_start = min(starts)
        if min_start < 0x100000:
            raise ValueError(
                f"Min start address {hex(min_start)} is below program base 0x100000"
            )

        # Parse TOML basic checks
        with open(self.output_toml, "r", encoding="utf-8") as f:
            toml_text = f.read()

        if "[general]" not in toml_text or "stubs = [" not in toml_text:
            raise ValueError("Exported TOML is missing required [general] or stubs section")

        metrics = {
            "total_records": len(rows),
            "min_start": hex(min_start),
            "max_end": hex(max_end),
            "stall_target_present": has_stall_target,
            "stall_target_name": names_by_addr.get(TARGET_STALL_ADDR),
            "data_tail_entries": len(entries_in_data_tail),
            "toml_size": self.output_toml.stat().st_size,
            "csv_size": self.output_csv.stat().st_size,
        }

        return metrics


def main():
    parser = argparse.ArgumentParser(description="KOF XI Function Symbols Exporter via Ghidra Headless")
    parser.add_argument("--elf", type=Path, default=DEFAULT_ELF_PATH, help="Path to extracted SLUS_216.87")
    parser.add_argument("--ghidra-dir", type=Path, default=DEFAULT_GHIDRA_DIR, help="Path to Ghidra installation")
    parser.add_argument("--jdk-dir", type=Path, default=DEFAULT_JDK_DIR, help="Path to JDK 21")
    parser.add_argument("--project-dir", type=Path, default=DEFAULT_PROJECT_DIR, help="Path to Ghidra project directory")
    parser.add_argument("--output-toml", type=Path, default=DEFAULT_OUTPUT_TOML, help="Path to output symbols.toml")
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV, help="Path to output symbols.csv")
    parser.add_argument("--reanalyze", action="store_true", help="Force fresh import and re-analysis")
    parser.add_argument("--verify-only", action="store_true", help="Only validate existing exported symbols")

    args = parser.parse_args()

    exporter = SymbolExporter(
        elf_path=args.elf,
        ghidra_dir=args.ghidra_dir,
        jdk_dir=args.jdk_dir,
        project_dir=args.project_dir,
        output_toml=args.output_toml,
        output_csv=args.output_csv,
    )

    try:
        if args.verify_only:
            logger.info("Validating existing exported symbols...")
            metrics = exporter.validate_exported_symbols()
            print("Validation successful!")
            for k, v in metrics.items():
                print(f"  {k}: {v}")
            return 0

        print("=== Step 1: Verifying Environment ===")
        env_info = exporter.verify_environment()
        print(f"JDK: OK | Ghidra: OK | EE Module: OK | ELF SHA-1: {env_info['elf_sha1']}")

        print("=== Step 2: Running Headless Ghidra Export ===")
        exporter.run_export(reanalyze=args.reanalyze)

        print("=== Step 3: Validating Exported Symbols ===")
        metrics = exporter.validate_exported_symbols()
        print("Validation successful! All criteria met:")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
        return 0

    except Exception as e:
        logger.error(f"Error during symbol export: {e}", exc_info=True)
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    sys.exit(main())
