import os
import unittest
import tempfile
import struct
import hashlib
from pathlib import Path

# Module to test
from tools.setup.extract_iso import IsoExtractor, EXPECTED_SLUS_SHA1, EXPECTED_VOLUME_ID

class TestIsoExtractor(unittest.TestCase):

    def test_invalid_iso_header_raises_error(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"NOT_AN_ISO_FILE" * 100)
            temp_path = f.name
        try:
            extractor = IsoExtractor(temp_path)
            with self.assertRaises(ValueError) as ctx:
                extractor.validate_pvd()
            self.assertIn("Not a valid ISO 9660", str(ctx.exception))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_dummy_dat_files_are_skipped(self):
        extractor = IsoExtractor("dummy.iso")
        self.assertTrue(extractor.should_skip_file("KOF_0000.DAT"))
        self.assertTrue(extractor.should_skip_file("KOF_0001.DAT"))
        self.assertTrue(extractor.should_skip_file("kof_0000.dat"))
        self.assertTrue(extractor.should_skip_file("KOF_0000.DAT;1"))
        self.assertFalse(extractor.should_skip_file("SLUS_216.87"))
        self.assertFalse(extractor.should_skip_file("SYSTEM.CNF"))
        self.assertFalse(extractor.should_skip_file("DATA/PL/PL00.BIN"))

    def test_executable_hash_validation(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"TEST_EXECUTABLE_DATA")
            temp_path = f.name
        try:
            extractor = IsoExtractor("dummy.iso")
            # Should fail with wrong hash
            self.assertFalse(extractor.verify_executable(temp_path, EXPECTED_SLUS_SHA1))
            # Should pass with matching hash
            correct_hash = hashlib.sha1(b"TEST_EXECUTABLE_DATA").hexdigest()
            self.assertTrue(extractor.verify_executable(temp_path, correct_hash))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_real_iso_if_present(self):
        real_iso = Path("private/ps2/PS2 - The King of Fighters XI.iso")
        if not real_iso.exists():
            self.skipTest("Real PS2 ISO not present in private/ps2/")

        extractor = IsoExtractor(str(real_iso))
        pvd_info = extractor.validate_pvd()
        self.assertEqual(pvd_info["standard_id"], b"CD001")
        self.assertEqual(pvd_info["volume_id"], EXPECTED_VOLUME_ID)

        file_list = extractor.list_files()
        filenames = [f["path"].upper() for f in file_list]

        # Verify key files exist in ISO
        self.assertIn("SLUS_216.87", filenames)
        self.assertIn("SYSTEM.CNF", filenames)
        self.assertIn("MODULES/CRI_ADXI.IRX", filenames)
        self.assertIn("DATA/ZDX/KOFXIBGM.AFS", filenames)

        # Verify DAT files are recognized in ISO
        self.assertIn("KOF_0000.DAT", filenames)
        self.assertIn("KOF_0001.DAT", filenames)

        # Verify DAT files are flagged to skip
        files_to_extract = [f for f in file_list if not extractor.should_skip_file(f["path"])]
        paths_to_extract = [f["path"].upper() for f in files_to_extract]
        self.assertNotIn("KOF_0000.DAT", paths_to_extract)
        self.assertNotIn("KOF_0001.DAT", paths_to_extract)

if __name__ == "__main__":
    unittest.main()
