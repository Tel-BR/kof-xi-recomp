#!/usr/bin/env python3
"""
ISO Extractor and Validator for KOF XI (PS2 Release - US SLUS-21687 v1.00).

Extracts game assets (~1.17 GB) directly from a user-supplied PS2 ISO image
while automatically omitting the dummy padding DAT files (KOF_0000.DAT and KOF_0001.DAT,
saving ~1.26 GB of disk space) per ADR-0003 and Ticket 12/18.

Verifies the integrity of the US release by hashing SLUS_216.87.
"""

import os
import sys
import struct
import hashlib
import argparse
from pathlib import Path

SECTOR_SIZE = 2048
PVD_SECTOR = 16

# Expected constants for SLUS-21687 v1.00 (US edition)
EXPECTED_VOLUME_ID = "KING_OF_FIGHTERS_XI"
EXPECTED_SLUS_SHA1 = "133f8c56283f0e255be995e894a3a7e6fe0c7b24"
EXPECTED_SLUS_CRC32 = "912B44D2"

# Files to explicitly skip (dummy padding on the outer edge of the DVD)
SKIP_FILES = {
    "KOF_0000.DAT",
    "KOF_0001.DAT",
}

class IsoExtractor:
    def __init__(self, iso_path: str = None):
        self.iso_path = Path(iso_path) if iso_path else None

    def _ensure_iso_exists(self):
        if not self.iso_path or not self.iso_path.exists():
            raise FileNotFoundError(f"ISO file not found: {self.iso_path}")

    def validate_pvd(self) -> dict:
        """Reads and validates the Primary Volume Descriptor (PVD)."""
        self._ensure_iso_exists()
        with open(self.iso_path, "rb") as f:
            f.seek(PVD_SECTOR * SECTOR_SIZE)
            pvd = f.read(SECTOR_SIZE)

        if len(pvd) < SECTOR_SIZE:
            raise ValueError(f"Not a valid ISO 9660 image: file too small ({len(pvd)} bytes)")

        pvd_type = pvd[0]
        standard_id = pvd[1:6]
        if standard_id != b"CD001" or pvd_type != 1:
            raise ValueError(f"Not a valid ISO 9660 image (magic: {standard_id!r}, type: {pvd_type})")

        volume_id = pvd[40:72].decode("ascii", errors="ignore").strip()

        # Root directory record at offset 156 (34 bytes minimum)
        root_record = pvd[156:156 + 34]
        root_lba, = struct.unpack_from("<I", root_record, 2)
        root_len, = struct.unpack_from("<I", root_record, 10)

        return {
            "standard_id": standard_id,
            "volume_id": volume_id,
            "root_lba": root_lba,
            "root_len": root_len,
        }

    def _clean_name(self, raw_name: bytes) -> str:
        """Strips ISO 9660 version suffix ';1' and converts to clean string."""
        name = raw_name.decode("ascii", errors="ignore")
        if ";1" in name:
            name = name.split(";1")[0]
        return name

    def should_skip_file(self, file_path: str) -> bool:
        """Returns True if file is dummy padding (KOF_0000.DAT or KOF_0001.DAT)."""
        base_name = Path(file_path).name.upper()
        if ";1" in base_name:
            base_name = base_name.split(";1")[0]
        return base_name in SKIP_FILES

    def list_files(self) -> list:
        """Traverses the ISO 9660 directory hierarchy and returns all file entries."""
        self._ensure_iso_exists()
        pvd = self.validate_pvd()
        files = []

        with open(self.iso_path, "rb") as f:
            dirs_to_visit = [("", pvd["root_lba"], pvd["root_len"])]

            while dirs_to_visit:
                curr_prefix, dir_lba, dir_len = dirs_to_visit.pop(0)

                f.seek(dir_lba * SECTOR_SIZE)
                dir_data = f.read(dir_len)

                offset = 0
                while offset < len(dir_data):
                    rec_len = dir_data[offset]
                    if rec_len == 0:
                        # Advance to next 2048 sector boundary
                        offset = ((offset // SECTOR_SIZE) + 1) * SECTOR_SIZE
                        continue

                    if offset + rec_len > len(dir_data):
                        break

                    lba, = struct.unpack_from("<I", dir_data, offset + 2)
                    size, = struct.unpack_from("<I", dir_data, offset + 10)
                    flags = dir_data[offset + 25]
                    name_len = dir_data[offset + 32]
                    name_raw = dir_data[offset + 33 : offset + 33 + name_len]

                    # Skip '.' (\x00) and '..' (\x01)
                    if name_raw not in (b"\x00", b"\x01"):
                        clean_name = self._clean_name(name_raw)
                        rel_path = f"{curr_prefix}/{clean_name}".lstrip("/")

                        is_directory = bool(flags & 2)
                        if is_directory:
                            dirs_to_visit.append((rel_path, lba, size))
                        else:
                            files.append({
                                "path": rel_path,
                                "lba": lba,
                                "size": size,
                            })

                    offset += rec_len

        return files

    def verify_executable(self, file_path: str, expected_sha1: str = EXPECTED_SLUS_SHA1) -> bool:
        """Computes SHA-1 of the specified file and matches against expected."""
        h = hashlib.sha1()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest().lower() == expected_sha1.lower()

    def extract_all(self, dest_dir: str, progress_callback=None) -> dict:
        """
        Extracts all real game assets to dest_dir, omitting dummy DAT files.
        Returns a summary dict with counts, total bytes, and verification status.
        """
        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)

        files = self.list_files()
        extracted_count = 0
        skipped_count = 0
        total_bytes = 0

        with open(self.iso_path, "rb") as f:
            for file_info in files:
                rel_path = file_info["path"]

                if self.should_skip_file(rel_path):
                    skipped_count += 1
                    if progress_callback:
                        progress_callback("skip", rel_path, file_info["size"])
                    continue

                out_file = dest_path / rel_path
                out_file.parent.mkdir(parents=True, exist_ok=True)

                f.seek(file_info["lba"] * SECTOR_SIZE)
                remaining = file_info["size"]

                with open(out_file, "wb") as out_f:
                    while remaining > 0:
                        chunk_size = min(65536, remaining)
                        data = f.read(chunk_size)
                        if not data:
                            raise IOError(f"Unexpected EOF while extracting {rel_path}")
                        out_f.write(data)
                        remaining -= chunk_size

                extracted_count += 1
                total_bytes += file_info["size"]
                if progress_callback:
                    progress_callback("extract", rel_path, file_info["size"])

        # Validate executable
        slus_path = dest_path / "SLUS_216.87"
        is_valid = False
        slus_sha1 = ""
        if slus_path.exists():
            h = hashlib.sha1()
            with open(slus_path, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            slus_sha1 = h.hexdigest().lower()
            is_valid = (slus_sha1 == EXPECTED_SLUS_SHA1.lower())

        return {
            "extracted_count": extracted_count,
            "skipped_count": skipped_count,
            "total_bytes_extracted": total_bytes,
            "slus_sha1": slus_sha1,
            "is_valid": is_valid,
        }

def main():
    parser = argparse.ArgumentParser(description="Extract and validate KOF XI PS2 ISO assets.")
    parser.add_argument("--iso", required=True, help="Path to User-supplied KOF XI PS2 ISO")
    parser.add_argument("--output", default="private/extracted", help="Destination folder (default: private/extracted)")
    parser.add_argument("--list-only", action="store_true", help="Only list files without extracting")
    args = parser.parse_args()

    extractor = IsoExtractor(args.iso)
    pvd = extractor.validate_pvd()
    print(f"ISO Volume: {pvd['volume_id']} (Valid ISO 9660)")

    if args.list_only:
        files = extractor.list_files()
        print(f"Total files found in ISO: {len(files)}")
        for f in files:
            skip_mark = "[SKIP DUMMY]" if extractor.should_skip_file(f["path"]) else "[EXTRACT]"
            print(f"  {skip_mark} {f['path']} ({f['size']:,} bytes)")
        return

    print(f"Extracting assets to: {args.output}")
    def log_progress(action, path, size):
        if action == "skip":
            print(f"  Skipping dummy padding: {path} ({size:,} bytes)")
        elif action == "extract":
            pass

    summary = extractor.extract_all(args.output, progress_callback=log_progress)
    print("\nExtraction Complete!")
    print(f"  Files Extracted: {summary['extracted_count']}")
    print(f"  Files Skipped:   {summary['skipped_count']} (saved ~1.26 GB)")
    print(f"  Extracted Size:  {summary['total_bytes_extracted'] / (1024*1024):.2f} MB")
    print(f"  Executable SHA-1:{summary['slus_sha1']}")
    print(f"  Integrity Check: {'PASSED (SLUS-21687 v1.00 US)' if summary['is_valid'] else 'FAILED'}")

    if not summary["is_valid"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
