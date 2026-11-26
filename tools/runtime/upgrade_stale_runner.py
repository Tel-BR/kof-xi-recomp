#!/usr/bin/env python3
"""
Bring stale recompiler output up to the current PS2Recomp-Fixer code generator.

The GPU runner compiles generated sources (`src/runner/`) that an older recompiler
produced. The current generator fixed R5900 semantics that this output still
gets wrong. The fixes cover menu and character-select graphics and ADX audio:

1. BLTZ/BGEZ/BLEZ/BGTZ (and their likely/link forms) test the whole 64-bit GPR.
   The stale output tested the low 32 bits, so libgcc's soft-float `__adddf3`
   kept a negative 64-bit mantissa difference positive: every rounded rotated
   sprite corner more than ~128 px left or above its pivot moved 255 px.
2. COP2 macro FMAC ops update the VU0 MAC flags and the Z/S status bits with their
   sticky copies (upstream PS2Recomp PR #292). Games read them with CFC2; a
   projection clip test that reads the sticky flags saw 0 and never clipped.
   A macro op that writes VF0 is undone: VF0 is (0,0,0,1).
3. LQC2 to VF0 has no effect on the hardware, so a VU0 context restore must not
   overwrite VF0.
4. COP1 SQRT.S reads ft. The stale output read fs, corrupting the ADX predictor.

The upgrade reads the disassembly comment the recompiler prints above every
instruction (`// 0xADDR: 0xRAW  mnemonic`), so each edit is keyed on the actual
instruction word, never on a guess about the C++ text. It is idempotent.

    python tools/runtime/upgrade_stale_runner.py private/tools/PS2Recomp-Fixer/third_party/src/PS2Recomp/ps2xRuntime/src/runner
    python tools/runtime/upgrade_stale_runner.py --check <runner dir>   # report only

Generated sources are game-derived and stay under private/.
"""

import argparse
import re
import sys
from pathlib import Path

INSTRUCTION = re.compile(r"^(\s*)// 0x([0-9a-fA-F]+): 0x([0-9a-fA-F]+)\s+(\S+)")
SIGN_BRANCH = re.compile(r"(const bool branch_taken_0x([0-9a-fA-F]+) = \()GPR_S32(\(ctx, \d+\) (?:<|>=|<=|>) 0\);)")
PC_LINE = re.compile(r"^\s*ctx->pc = 0x[0-9a-fA-F]+u;\s*$")
VF0_LOAD = re.compile(r"^(\s*)ctx->vu0_vf\[0\] = _mm_castsi128_ps\(.*\);\s*$")
SQRT_SOURCE = re.compile(r"FPU_SQRT_S\(ctx->f\[\d+\]\)")

VF0_RESET = "ctx->vu0_vf[0] = _mm_setr_ps(0.0f, 0.0f, 0.0f, 1.0f);"
OP_COP2 = 0x12
OP_LQC2 = 0x36
OP_REGIMM = 0x01
REGIMM_SIGN = {0x00, 0x01, 0x02, 0x03, 0x10, 0x11, 0x12, 0x13}  # BLTZ/BGEZ(L) and the AL(L) forms
OPS_SIGN = {0x06, 0x07, 0x16, 0x17}  # BLEZ, BGTZ, BLEZL, BGTZL


def opcode(raw):
    return raw >> 26


def rt_field(raw):
    return (raw >> 16) & 0x1F


def is_sign_branch(raw):
    return (opcode(raw) == OP_REGIMM and rt_field(raw) in REGIMM_SIGN) or opcode(raw) in OPS_SIGN


def macro_op_dest(raw):
    """What a COP2 macro op writes: (sets_mac, to_acc, vf). Mirrors the generator's macroOpDest."""
    funct = raw & 0x3F
    ft = rt_field(raw)
    fd = (raw >> 6) & 0x1F
    if funct < 0x3C:
        if funct >= 0x30:
            return False, False, -1  # integer ops and VCALLMS
        max_min = 0x10 <= funct <= 0x17 or funct in (0x1D, 0x1F, 0x2B, 0x2F)
        return not max_min, False, fd
    op2 = (((raw >> 6) & 0x1F) << 2) | (raw & 0x3)
    acc_op = (op2 <= 0x0F or 0x18 <= op2 <= 0x1C or op2 == 0x1E or 0x20 <= op2 <= 0x2A
              or op2 in (0x2C, 0x2D, 0x2E))
    if acc_op:
        return True, True, -1
    if 0x10 <= op2 <= 0x17 or op2 in (0x1D, 0x30, 0x31, 0x34, 0x36, 0x3D):
        return False, False, ft
    return False, False, -1


def is_macro_op(raw):
    return opcode(raw) == OP_COP2 and (raw >> 25) & 1


def copy_pc_line(lines, i, out):
    """Copy the optional `ctx->pc = ...;` line after a disassembly comment; return the next index."""
    if i < len(lines) and PC_LINE.match(lines[i]):
        out.append(lines[i])
        return i + 1
    return i


def upgrade_source(text):
    """Return (upgraded text, counts of each kind of edit)."""
    stats = {"sign_branches": 0, "mac_flags": 0, "vf0_restores": 0, "lqc2_vf0": 0, "sqrt_sources": 0}
    lines = text.split("\n")
    # Entry points repeat code, so a branch condition can sit far from its disassembly comment: look the
    # branch up by the address in its variable name.
    words = {}
    for line in lines:
        m = INSTRUCTION.match(line)
        if m:
            words.setdefault(int(m.group(2), 16), int(m.group(3), 16))
    out = []
    i = 0
    raw = None  # instruction word of the most recent disassembly comment
    while i < len(lines):
        line = lines[i]
        m = INSTRUCTION.match(line)
        if m:
            raw = int(m.group(3), 16)
            out.append(line)
            i += 1
            if opcode(raw) == 0x11 and (raw >> 21) & 0x1F == 0x10 and raw & 0x3F == 4:
                i = copy_pc_line(lines, i, out)
                if i < len(lines):
                    body = lines[i]
                    fixed = SQRT_SOURCE.sub(f"FPU_SQRT_S(ctx->f[{rt_field(raw)}])", body)
                    if fixed != body:
                        out.append(fixed)
                        stats["sqrt_sources"] += 1
                        i += 1
            elif opcode(raw) == OP_LQC2 and rt_field(raw) == 0:
                i = copy_pc_line(lines, i, out)
                if i < len(lines):
                    load = VF0_LOAD.match(lines[i])
                    if load:
                        out.append(f"{load.group(1)}// LQC2 to VF0 ignored (VF0 is hardwired to (0,0,0,1))")
                        stats["lqc2_vf0"] += 1
                        i += 1
            elif is_macro_op(raw):
                sets_mac, to_acc, vf = macro_op_dest(raw)
                if not sets_mac and vf != 0:
                    continue
                i = copy_pc_line(lines, i, out)
                if i >= len(lines) or "vu0_" not in lines[i]:
                    continue  # not the expected one-line translation; leave it as is
                body = lines[i]
                out.append(body)
                i += 1
                indent = re.match(r"^(\s*)", body).group(1)
                dest = (raw >> 21) & 0xF
                epilogue = []
                if sets_mac:
                    target = "ctx->vu0_acc" if to_acc else f"ctx->vu0_vf[{vf}]"
                    epilogue.append(f"PS2_VU0_SET_MAC(ctx, {target}, 0x{dest:X}u);")
                if vf == 0:
                    epilogue.append(VF0_RESET)
                following = [lines[j].strip() for j in range(i, min(i + len(epilogue), len(lines)))]
                if following == epilogue:
                    continue  # already upgraded
                out.extend(indent + e for e in epilogue)
                stats["mac_flags"] += int(sets_mac)
                stats["vf0_restores"] += int(vf == 0)
            continue
        branch = SIGN_BRANCH.search(line)
        if branch and is_sign_branch(words.get(int(branch.group(2), 16), 0)):
            line = SIGN_BRANCH.sub(r"\1GPR_S64\3", line)
            stats["sign_branches"] += 1
        out.append(line)
        i += 1
    return "\n".join(out), stats


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("runner_dir", type=Path)
    parser.add_argument("--check", action="store_true", help="report what would change, write nothing")
    args = parser.parse_args(argv)
    totals = {"files": 0}
    for path in sorted(args.runner_dir.glob("*.cpp")):
        with path.open(encoding="utf-8", errors="surrogateescape", newline="") as f:
            original = f.read()
        eol = "\r\n" if "\r\n" in original else "\n"
        text = original.replace("\r\n", "\n")
        new, stats = upgrade_source(text)
        if new == text:
            continue
        new = new.replace("\n", eol)
        totals["files"] += 1
        for k, v in stats.items():
            totals[k] = totals.get(k, 0) + v
        if not args.check:
            with path.open("w", encoding="utf-8", errors="surrogateescape", newline="") as f:
                f.write(new)
    print(" ".join(f"{k}={v}" for k, v in totals.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
