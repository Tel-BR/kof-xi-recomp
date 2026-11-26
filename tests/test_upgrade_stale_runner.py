#!/usr/bin/env python3
"""Tests for the stale generated-code upgrade (issue #12, rotating 3D layer).

The snippets are synthetic: invented addresses and registers, real R5900 instruction
encodings, laid out the way the recompiler prints them. No game code.
"""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from tools.runtime.upgrade_stale_runner import main, upgrade_source

SIGN_BRANCH = """\
    // 0x100000: 0x5c20027  bltzl       $t6, . + 4 + (0x27 << 2)
    ctx->pc = 0x100000u;
    {
        const bool branch_taken_0x100000 = (GPR_S32(ctx, 14) < 0);
"""

# Entry points repeat code: the condition can sit far from its branch's disassembly comment.
SIGN_BRANCH_ELSEWHERE = """\
    // 0x100100: 0x441000c  bgez        $v0, . + 4 + (0xC << 2)
    // 0x100104: 0x200282d  daddu       $a1, $s0, $zero (Delay Slot)
    SET_GPR_U64(ctx, 5, (uint64_t)GPR_U64(ctx, 16) + (uint64_t)GPR_U64(ctx, 0));
    ctx->pc = 0x100100u;
    {
        const bool branch_taken_0x100100 = (GPR_S32(ctx, 2) >= 0);
"""

EQUAL_BRANCH = """\
    // 0x100010: 0x10430003  beq         $v0, $v1, . + 4 + (0x3 << 2)
    ctx->pc = 0x100010u;
    {
        const bool branch_taken_0x100010 = (GPR_S32(ctx, 2) < 0);
"""

VSUB = """\
    // 0x100200: 0x4bab4b2c  vsub.xyw    $vf12, $vf9, $vf11
    ctx->pc = 0x100200u;
    { __m128 res = PS2_VSUB(ctx->vu0_vf[9], ctx->vu0_vf[11]); ctx->vu0_vf[12] = res; }
    // 0x100204: 0x0  nop
"""

VMULAX = """\
    // 0x100300: 0x4be821bc  vmulax.xyzw $ACC, $vf4, $vf8x
    ctx->pc = 0x100300u;
    { ctx->vu0_acc = PS2_VMUL(ctx->vu0_vf[4], ctx->vu0_vf[8]); }
"""

# VMAX.xyzw vf1, vf1, vf2: COP2 macro funct 0x2B leaves the flags alone.
VMAX = """\
    // 0x100400: 0x4be2086b  vmax.xyzw   $vf1, $vf1, $vf2
    ctx->pc = 0x100400u;
    { ctx->vu0_vf[1] = ps2_vu_max_ps(ctx->vu0_vf[1], ctx->vu0_vf[2]); }
"""

VSUB_TO_VF0 = """\
    // 0x100500: 0x4be0002c  vsub.xyzw   $vf0, $vf0, $vf0
    ctx->pc = 0x100500u;
    { ctx->vu0_vf[0] = PS2_VSUB(ctx->vu0_vf[0], ctx->vu0_vf[0]); }
"""

LQC2_VF0 = """\
    // 0x100600: 0xda200000  lqc2        $vf0, 0x0($s1)
    ctx->pc = 0x100600u;
    ctx->vu0_vf[0] = _mm_castsi128_ps(READ128(ADD32(GPR_U32(ctx, 17), 0)));
    // 0x100604: 0xda210010  lqc2        $vf1, 0x10($s1)
    ctx->pc = 0x100604u;
    ctx->vu0_vf[1] = _mm_castsi128_ps(READ128(ADD32(GPR_U32(ctx, 17), 16)));
"""

DELAY_SLOT_VSUB = """\
            ctx->in_delay_slot = true;
            // 0x100700: 0x4bab4b2c  vsub.xyw    $vf12, $vf9, $vf11 (Delay Slot)
            { __m128 res = PS2_VSUB(ctx->vu0_vf[9], ctx->vu0_vf[11]); ctx->vu0_vf[12] = res; }
            ctx->in_delay_slot = false;
"""


class TestSignBranches(unittest.TestCase):

    def test_sign_branches_compare_the_whole_64_bit_register(self):
        text, stats = upgrade_source(SIGN_BRANCH)
        self.assertIn("(GPR_S64(ctx, 14) < 0)", text)
        self.assertNotIn("GPR_S32", text)
        self.assertEqual(stats["sign_branches"], 1)

    def test_the_branch_is_found_by_address_when_its_comment_is_elsewhere(self):
        text, stats = upgrade_source(SIGN_BRANCH_ELSEWHERE)
        self.assertIn("(GPR_S64(ctx, 2) >= 0)", text)
        self.assertEqual(stats["sign_branches"], 1)

    def test_other_branches_are_left_alone(self):
        text, stats = upgrade_source(EQUAL_BRANCH)
        self.assertEqual(text, EQUAL_BRANCH)
        self.assertEqual(stats["sign_branches"], 0)


class TestVu0MacroFlags(unittest.TestCase):

    def test_fmac_result_updates_the_flags_for_its_fields(self):
        text, stats = upgrade_source(VSUB)
        lines = text.splitlines()
        self.assertEqual(lines[3].strip(), "PS2_VU0_SET_MAC(ctx, ctx->vu0_vf[12], 0xDu);")
        self.assertEqual(stats["mac_flags"], 1)

    def test_accumulator_ops_update_the_flags_from_acc(self):
        text, _ = upgrade_source(VMULAX)
        self.assertIn("PS2_VU0_SET_MAC(ctx, ctx->vu0_acc, 0xFu);", text)

    def test_max_and_mini_leave_the_flags_alone(self):
        text, stats = upgrade_source(VMAX)
        self.assertEqual(text, VMAX)
        self.assertEqual(stats["mac_flags"], 0)

    def test_a_write_to_vf0_is_undone(self):
        text, stats = upgrade_source(VSUB_TO_VF0)
        lines = text.splitlines()
        self.assertEqual(lines[3].strip(), "PS2_VU0_SET_MAC(ctx, ctx->vu0_vf[0], 0xFu);")
        self.assertEqual(lines[4].strip(), "ctx->vu0_vf[0] = _mm_setr_ps(0.0f, 0.0f, 0.0f, 1.0f);")
        self.assertEqual(stats["vf0_restores"], 1)

    def test_delay_slot_ops_get_the_same_epilogue(self):
        text, _ = upgrade_source(DELAY_SLOT_VSUB)
        lines = text.splitlines()
        self.assertEqual(lines[3], "            PS2_VU0_SET_MAC(ctx, ctx->vu0_vf[12], 0xDu);")
        self.assertEqual(lines[4], "            ctx->in_delay_slot = false;")


class TestLqc2ToVf0(unittest.TestCase):

    def test_lqc2_to_vf0_is_dropped_and_other_registers_still_load(self):
        text, stats = upgrade_source(LQC2_VF0)
        self.assertNotIn("ctx->vu0_vf[0] = _mm_castsi128_ps", text)
        self.assertIn("// LQC2 to VF0 ignored", text)
        self.assertIn("ctx->vu0_vf[1] = _mm_castsi128_ps", text)
        self.assertEqual(stats["lqc2_vf0"], 1)


class TestIdempotence(unittest.TestCase):

    def test_a_second_pass_changes_nothing(self):
        source = SIGN_BRANCH + VSUB + VSUB_TO_VF0 + LQC2_VF0 + DELAY_SLOT_VSUB
        once, _ = upgrade_source(source)
        twice, stats = upgrade_source(once)
        self.assertEqual(twice, once)
        self.assertEqual(sum(stats.values()), 0)


class TestRunnerDirectory(unittest.TestCase):

    def test_rewrites_in_place_keeping_crlf_and_a_rerun_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "FUN_00100000_0x100000.cpp"
            path.write_bytes(SIGN_BRANCH.replace("\n", "\r\n").encode())
            with contextlib.redirect_stdout(io.StringIO()):
                main([tmp])
            data = path.read_bytes()
            self.assertIn(b"GPR_S64(ctx, 14) < 0);\r\n", data)
            self.assertNotIn(b"\r\r", data)
            report = io.StringIO()
            with contextlib.redirect_stdout(report):
                main([tmp])
            self.assertEqual(report.getvalue().strip(), "files=0")
            self.assertEqual(path.read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
