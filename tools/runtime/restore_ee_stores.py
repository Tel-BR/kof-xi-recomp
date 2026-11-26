#!/usr/bin/env python3
"""Restore confirmed analyzer NOPs from a user-supplied ELF in private runner sources."""

import argparse
from pathlib import Path
import re
import struct


def read_store_instructions(elf, addresses):
    if elf[:6] != b"\x7fELF\x01\x01" or len(elf) < 52:
        raise ValueError("expected a little-endian ELF32")
    machine, = struct.unpack_from("<H", elf, 18)
    table, = struct.unpack_from("<I", elf, 28)
    stride, count = struct.unpack_from("<HH", elf, 42)
    if machine != 8 or stride < 32 or table + count * stride > len(elf):
        raise ValueError("invalid MIPS ELF program headers")
    segments = [struct.unpack_from("<8I", elf, table + i * stride) for i in range(count)]
    stores = {}
    for address in addresses:
        for kind, offset, start, _, size, _, flags, _ in segments:
            if kind == 1 and flags & 1 and start <= address <= start + size - 4:
                index = offset + address - start
                if address % 4 or index + 4 > len(elf):
                    raise ValueError(f"invalid file offset for {address:#x}")
                word, = struct.unpack_from("<I", elf, index)
                if word >> 26 != 0x2B:
                    raise ValueError(f"{address:#x} does not contain an EE SW instruction")
                stores[address] = word
                break
        else:
            raise ValueError(f"{address:#x} is outside the executable ELF segments")
    return stores


def restore_sources(runner, stores):
    names = "|".join(f"{address:x}" for address in sorted(stores))
    comments = re.compile(rf"(?im)// 0x({names}):([^\r\n]*)")
    existing = re.compile(
        rf"(?im)ctx->pc = 0x({names})u;\r?\n"
        r"(?:[ \t]*(?:ctx->(?:in_delay_slot|branch_pc) = [^;]+;|//[^\r\n]*)\r?\n)*"
        r"[ \t]*WRITE32\("
    )
    nop = re.compile(r"([ \t]*\r?\n(?:[ \t]*ctx->pc = [^;]+;\r?\n)?[ \t]*)// NOP\b")
    seen = set()
    edits = {}
    for path in runner.glob("*.cpp"):
        original = path.read_bytes().decode("utf-8", errors="surrogateescape")
        seen.update(int(match[1], 16) for match in existing.finditer(original))
        changes = []
        for comment in comments.finditer(original):
            address = int(comment[1], 16)
            seen.add(address)
            if not re.match(r"\s*0x0+\s+nop\b", comment[2]):
                continue
            body = nop.match(original, comment.end())
            if body is None:
                raise ValueError(f"unrecognized NOP translation at {address:#x} in {path}")
            word = stores[address]
            base = (word >> 21) & 31
            value = (word >> 16) & 31
            displacement = (word & 0xFFFF) - (0x10000 if word & 0x8000 else 0)
            restored = (
                f"// {address:#x}: {word:#x}  sw  (restored from local ELF)"
                f"{body[1]}WRITE32(ADD32(GPR_U32(ctx, {base}), {displacement}), GPR_U32(ctx, {value}));"
            )
            changes.append((comment.start(), body.end(), restored))
        if changes:
            for start, end, replacement in reversed(changes):
                original = original[:start] + replacement + original[end:]
            edits[path] = original
    missing = stores.keys() - seen
    if missing:
        raise ValueError("missing generated store sites: " + ", ".join(f"{addr:#x}" for addr in sorted(missing)))
    for path, source in edits.items():
        path.write_bytes(source.encode("utf-8", errors="surrogateescape"))
    return len(edits)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("elf", type=Path)
    parser.add_argument("runner", type=Path)
    parser.add_argument("addresses", nargs="+", type=lambda value: int(value, 0))
    args = parser.parse_args()
    private = Path(__file__).resolve().parents[2] / "private"
    if not args.runner.resolve().is_relative_to(private):
        parser.error("runner sources must be under the ignored private directory")
    try:
        stores = read_store_instructions(args.elf.read_bytes(), args.addresses)
        count = restore_sources(args.runner, stores)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Updated {count} private runner files.")


if __name__ == "__main__":
    main()
