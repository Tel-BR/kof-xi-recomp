#!/usr/bin/env python3
"""Tests for the closed-loop menu probe's frame classifiers (issue #12).

Frames are synthetic arrays shaped like the 640x448 runtime captures; no game images.
"""

import unittest

import numpy as np

from tools.runtime.closed_loop import ROWS, apply_fps_floor, median_fps, menu_row, mode_screen_visible, title_score

ORANGE = (240, 150, 60)


def blank(color=(0, 0, 0)):
    frame = np.zeros((448, 640, 3), dtype=np.uint8)
    frame[:, :] = color
    return frame


def menu(highlighted):
    frame = blank((150, 200, 40))
    frame[6:56, 14:318] = ORANGE
    top, bottom = ROWS[highlighted]
    frame[top:bottom, 40:290] = ORANGE
    return frame


def restored_menu_mid_animation():
    """The restored main menu (white base, cyan fan) while no row is highlighted."""
    frame = blank((255, 255, 255))
    frame[60:440, 200:640] = (90, 200, 230)
    frame[6:56, 14:318] = ORANGE
    return frame


def select_screen():
    frame = blank((255, 255, 255))
    frame[40:280, 0:240] = (200, 30, 30)    # a portrait
    frame[300:440, 0:640:40] = (30, 90, 200)  # icon columns
    return frame


class TestMenuRow(unittest.TestCase):

    def test_reads_the_highlighted_row(self):
        self.assertEqual(menu_row(menu("TEAM")), "TEAM")
        self.assertEqual(menu_row(menu("ARCADE")), "ARCADE")

    def test_anything_without_the_orange_header_is_not_the_menu(self):
        self.assertIsNone(menu_row(select_screen()))
        self.assertIsNone(menu_row(blank()))


class TestModeScreenVisible(unittest.TestCase):

    def test_a_lit_colourful_screen_after_the_menu_is_visible(self):
        self.assertTrue(mode_screen_visible(select_screen()))

    def test_the_restored_menu_without_a_highlighted_row_is_not(self):
        self.assertFalse(mode_screen_visible(restored_menu_mid_animation()))

    def test_black_white_and_the_menu_itself_are_not(self):
        self.assertFalse(mode_screen_visible(blank()))
        self.assertFalse(mode_screen_visible(blank((255, 255, 255))))
        self.assertFalse(mode_screen_visible(menu("ARCADE")))


class TestTitleScore(unittest.TestCase):

    def test_a_frame_matching_the_reference_green_logo_scores_one(self):
        frame = blank()
        frame[100:300, 200:440] = (40, 200, 40)
        self.assertAlmostEqual(title_score(frame, [frame]), 1.0)
        self.assertEqual(title_score(blank(), [frame]), 0.0)


class TestFpsFloor(unittest.TestCase):

    def test_a_green_run_below_the_floor_turns_red(self):
        self.assertEqual(apply_fps_floor("GREEN title+menu+nav+mode_visible", 40.0, 45.0),
                         "RED FPS: median 40.0 < floor 45.0")
        self.assertEqual(apply_fps_floor("GREEN title+menu+nav+mode_visible", 50.6, 45.0),
                         "GREEN title+menu+nav+mode_visible")
        self.assertEqual(apply_fps_floor("GREEN title+menu+nav+mode_visible", None, 45.0),
                         "RED FPS: no frame-rate samples")

    def test_an_earlier_red_verdict_is_kept(self):
        self.assertEqual(apply_fps_floor("RED MODE_BLACK: x", 30.0, 45.0), "RED MODE_BLACK: x")


class TestMedianFps(unittest.TestCase):

    def test_uses_samples_after_boot(self):
        err = "\n".join(f"[fps] field {f}: {r} game frames/s, 59.9 fields/s" for f, r in
                        [(300, 20.0), (900, 58.0), (1200, 60.0), (1500, 59.0)])
        self.assertEqual(median_fps(err), 59.0)
        self.assertIsNone(median_fps("no samples"))


if __name__ == "__main__":
    unittest.main()
