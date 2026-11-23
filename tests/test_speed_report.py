#!/usr/bin/env python3
"""Tests for the runtime speed and audio report (ticket 13 feedback loop)."""

import unittest

from tools.runtime.speed_report import GREEN_THRESHOLD, summarize


def heartbeat(tick, threads):
    lines = [f"[heartbeat] vsyncTick={tick} threads={threads}"]
    lines += [f"  [th {i}] status=2 wait=1 pc=0x0 ra=0x0 sp=0x0" for i in range(1, threads + 1)]
    return "\n".join(lines)


def log(*beats):
    return "\n".join(heartbeat(t, n) for t, n in beats) + "\n"


class TestSummarize(unittest.TestCase):

    def test_median_counts_only_seconds_after_the_game_threads_start(self):
        out = log((60, 1), (120, 1), (180, 5), (205, 5), (231, 5), (256, 5))
        report = summarize(out)
        self.assertEqual(report.in_game_seconds, 3)
        self.assertEqual(report.median_vsyncs_per_second, 25)
        self.assertEqual(report.verdict, "RED")

    def test_full_speed_is_green(self):
        out = log((100, 5), (160, 5), (219, 5), (279, 5))
        report = summarize(out)
        self.assertEqual(report.median_vsyncs_per_second, 60)
        self.assertGreaterEqual(report.median_vsyncs_per_second, GREEN_THRESHOLD)
        self.assertEqual(report.verdict, "GREEN")

    def test_no_in_game_seconds_gives_no_data(self):
        report = summarize(log((60, 1), (120, 1)))
        self.assertEqual(report.in_game_seconds, 0)
        self.assertIsNone(report.median_vsyncs_per_second)
        self.assertEqual(report.verdict, "NO DATA")

    def test_a_stalled_game_reports_zero(self):
        report = summarize(log((500, 5), (520, 5), (520, 5), (520, 5)))
        self.assertEqual(report.median_vsyncs_per_second, 0)

    def test_min_threads_is_configurable(self):
        out = log((0, 1), (30, 1), (60, 1))
        self.assertEqual(summarize(out, min_threads=1).median_vsyncs_per_second, 30)

    def test_counts_adx_output_failures_in_stderr(self):
        err = (
            "[ps2xIOP] [IOP printf] E0110120: ioprna_create_rmt: can't create PSM\n"
            "vfprintf error: Invalid file handle\n"
            "[ps2xIOP] [IOP printf] E0110120: ioprna_create_rmt: can't create PSM\n"
        )
        report = summarize(log((0, 5), (20, 5)), err)
        self.assertEqual(report.adx_output_failures, 2)

    def test_without_stderr_the_audio_signal_is_unknown_not_zero(self):
        report = summarize(log((0, 5), (26, 5)))
        self.assertIsNone(report.adx_output_failures)
        self.assertIn("adx output failures=-", report.format("run"))

    def test_format_is_one_line_with_the_verdict(self):
        text = summarize(log((0, 5), (26, 5), (52, 5)), "").format("probe")
        self.assertEqual(
            text,
            "[probe] in-game seconds=2 median vsyncs/s=26 adx output failures=0 verdict=RED",
        )


if __name__ == "__main__":
    unittest.main()
