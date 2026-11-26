import struct
import tempfile
import unittest
from pathlib import Path

from tools.runtime.restore_ee_stores import read_store_instructions, restore_sources


class StoreRepairTest(unittest.TestCase):
    def test_restores_only_confirmed_store_and_preserves_delay_slot(self):
        address = 0x100000
        word = (0x2B << 26) | (4 << 21) | (5 << 16) | 0xFFFC
        elf = bytearray(88)
        elf[:6] = b"\x7fELF\x01\x01"
        struct.pack_into("<H", elf, 18, 8)
        struct.pack_into("<I", elf, 28, 52)
        struct.pack_into("<HH", elf, 42, 32, 1)
        struct.pack_into("<8I", elf, 52, 1, 84, address, 0, 4, 4, 5, 4)
        struct.pack_into("<I", elf, 84, word)
        stores = read_store_instructions(elf, [address])
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "generated.cpp"
            source.write_bytes(
                b"    ctx->in_delay_slot = true;\r\n"
                b"    // 0x100000: 0x0  nop (Delay Slot)\r\n"
                b"    // NOP\r\n"
                b"    ctx->in_delay_slot = false;\r\n"
                b"    // 0x100004: 0x0  nop\r\n"
                b"    // NOP\r\n"
            )
            self.assertEqual(restore_sources(Path(tmp), stores), 1)
            self.assertIn(b"WRITE32(ADD32(GPR_U32(ctx, 4), -4), GPR_U32(ctx, 5));\r\n", source.read_bytes())
            self.assertEqual(source.read_bytes().count(b"// NOP"), 1)
            self.assertEqual(restore_sources(Path(tmp), stores), 0)
        with self.assertRaisesRegex(ValueError, "outside the executable"):
            read_store_instructions(elf, [address + 4])
