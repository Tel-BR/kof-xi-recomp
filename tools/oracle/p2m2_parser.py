#!/usr/bin/env python3
"""
Parser, validator, and slicer for PCSX2 Input Recording (.p2m2) files.

The .p2m2 container stores frame-by-frame controller inputs for PCSX2:
- Header (606 bytes):
  * offset 0 (1 byte): format version (expected 0x01)
  * offset 1..50 (50 bytes): emulator version tag (e.g., 'PCSX2-v2.8.2')
  * offset 51..305 (255 bytes): author string
  * offset 306..560 (255 bytes): game title string
  * offset 561..564 (4 bytes): total_frames (uint32-LE)
  * offset 565..568 (4 bytes): undo_count (uint32-LE)
  * offset 569 (1 byte): savestate_flag
  * offset 570..605 (36 bytes): reserved padding
- Payload (36 bytes per frame):
  * Exactly two 18-byte DualShock 2 controller state packets:
    - Packet 0: Port 0 (Player 1)
    - Packet 1: Port 1 (Player 2)
  * 18-byte DualShock 2 packet layout:
    - byte 0..1: buttons bitmask (uint16-LE, active-low: 0 = pressed, 1 = released)
    - byte 2: Right Stick X (0..255, center 127/128)
    - byte 3: Right Stick Y (0..255, center 127/128)
    - byte 4: Left Stick X (0..255, center 127/128)
    - byte 5: Left Stick Y (0..255, center 127/128)
    - byte 6..17: 12 button pressure values (Right, Left, Up, Down,
      Triangle, Circle, Cross, Square, L1, R1, L2, R2)
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, List, Optional, Tuple, Union


HEADER_SIZE = 606
FRAME_PAYLOAD_SIZE = 36
PACKET_SIZE = 18

BUTTON_NAMES = [
    (1 << 0, "SELECT"),
    (1 << 1, "L3"),
    (1 << 2, "R3"),
    (1 << 3, "START"),
    (1 << 4, "UP"),
    (1 << 5, "RIGHT"),
    (1 << 6, "DOWN"),
    (1 << 7, "LEFT"),
    (1 << 8, "L2"),
    (1 << 9, "R2"),
    (1 << 10, "L1"),
    (1 << 11, "R1"),
    (1 << 12, "TRIANGLE"),
    (1 << 13, "CIRCLE"),
    (1 << 14, "CROSS"),
    (1 << 15, "SQUARE"),
]


@dataclass(frozen=True)
class DS2ControllerState:
    """Decoded 18-byte DualShock 2 controller packet."""

    buttons: int  # 16-bit mask, active-low (0 = pressed)
    rx: int
    ry: int
    lx: int
    ly: int
    pressures: Tuple[int, ...]  # 12 pressure bytes

    @property
    def pressed_button_names(self) -> List[str]:
        """Names of currently pressed buttons (bits that are 0 in active-low mask)."""
        return [name for mask, name in BUTTON_NAMES if (self.buttons & mask) == 0]

    def is_button_pressed(self, mask: int) -> bool:
        return (self.buttons & mask) == 0

    def raw_bytes(self) -> bytes:
        """Encode controller state back into 18 bytes."""
        hdr = struct.pack("<H4B", self.buttons, self.rx, self.ry, self.lx, self.ly)
        pressures = bytes(self.pressures) if len(self.pressures) == 12 else bytes(12)
        return hdr + pressures


@dataclass(frozen=True)
class P2M2Frame:
    """One frame of controller replay data (two DualShock 2 packets)."""

    frame_index: int
    port0: DS2ControllerState
    port1: DS2ControllerState

    def raw_bytes(self) -> bytes:
        return self.port0.raw_bytes() + self.port1.raw_bytes()


@dataclass
class P2M2Header:
    """Decoded 606-byte .p2m2 header."""

    version: int
    emulator_tag: str
    author: str
    game_title: str
    total_frames: int
    undo_count: int = 0
    savestate_flag: int = 0
    raw_header_bytes: Optional[bytes] = None

    def pack(self) -> bytes:
        """Pack header into 606 bytes."""
        if self.raw_header_bytes and len(self.raw_header_bytes) == HEADER_SIZE:
            buf = bytearray(self.raw_header_bytes)
            struct.pack_into("<I", buf, 561, self.total_frames)
            return bytes(buf)

        buf = bytearray(HEADER_SIZE)
        buf[0] = self.version & 0xFF
        tag_bytes = self.emulator_tag.encode("utf-8")[:50]
        buf[1 : 1 + len(tag_bytes)] = tag_bytes
        author_bytes = self.author.encode("utf-8")[:255]
        buf[51 : 51 + len(author_bytes)] = author_bytes
        title_bytes = self.game_title.encode("utf-8")[:255]
        buf[306 : 306 + len(title_bytes)] = title_bytes
        struct.pack_into("<I", buf, 561, self.total_frames)
        struct.pack_into("<I", buf, 565, self.undo_count)
        buf[569] = self.savestate_flag & 0xFF
        return bytes(buf)


def decode_ds2_packet(packet: bytes) -> DS2ControllerState:
    """Decode an 18-byte DualShock 2 packet."""
    if len(packet) < PACKET_SIZE:
        packet = packet.ljust(PACKET_SIZE, b"\x00")
    buttons, rx, ry, lx, ly = struct.unpack_from("<H4B", packet, 0)
    pressures = tuple(packet[6:18])
    return DS2ControllerState(buttons=buttons, rx=rx, ry=ry, lx=lx, ly=ly, pressures=pressures)


class P2M2Replay:
    """
    Representation of a PCSX2 .p2m2 input recording file.
    """

    def __init__(self, header: P2M2Header, raw_payload: bytes):
        self.header = header
        self.raw_payload = raw_payload
        self._validate()

    def _validate(self) -> None:
        expected_len = self.header.total_frames * FRAME_PAYLOAD_SIZE
        if len(self.raw_payload) < expected_len:
            raise ValueError(
                f"Payload size {len(self.raw_payload)} bytes is smaller than expected "
                f"{expected_len} bytes for {self.header.total_frames} frames"
            )

    @property
    def total_frames(self) -> int:
        return self.header.total_frames

    def get_frame(self, frame_index: int) -> P2M2Frame:
        """Get decoded inputs for a specific frame index (0-based)."""
        if frame_index < 0 or frame_index >= self.header.total_frames:
            raise IndexError(f"Frame {frame_index} out of range [0, {self.header.total_frames})")
        offset = frame_index * FRAME_PAYLOAD_SIZE
        p0_raw = self.raw_payload[offset : offset + PACKET_SIZE]
        p1_raw = self.raw_payload[offset + PACKET_SIZE : offset + FRAME_PAYLOAD_SIZE]
        return P2M2Frame(
            frame_index=frame_index,
            port0=decode_ds2_packet(p0_raw),
            port1=decode_ds2_packet(p1_raw),
        )

    def truncate(self, target_frames: int) -> P2M2Replay:
        """
        Produce a truncated copy of the replay running for exactly target_frames.
        Preserves header metadata while setting total_frames at offset 561 and
        slicing the payload to target_frames * 36 bytes.
        """
        if target_frames < 0 or target_frames > self.header.total_frames:
            raise ValueError(
                f"Target frames {target_frames} invalid; must be between 0 and {self.header.total_frames}"
            )

        new_header = P2M2Header(
            version=self.header.version,
            emulator_tag=self.header.emulator_tag,
            author=self.header.author,
            game_title=self.header.game_title,
            total_frames=target_frames,
            undo_count=self.header.undo_count,
            savestate_flag=self.header.savestate_flag,
            raw_header_bytes=self.header.raw_header_bytes,
        )
        new_payload = self.raw_payload[: target_frames * FRAME_PAYLOAD_SIZE]
        return P2M2Replay(new_header, new_payload)

    def write(self, dest: Union[str, Path, BinaryIO]) -> int:
        """Write the .p2m2 file to disk or binary stream. Returns total bytes written."""
        data = self.header.pack() + self.raw_payload
        if hasattr(dest, "write"):
            return dest.write(data)  # type: ignore

        path = Path(dest)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            return f.write(data)

    @classmethod
    def load(cls, source: Union[str, Path, bytes]) -> P2M2Replay:
        """Load and parse a .p2m2 file from file path or byte buffer."""
        if isinstance(source, (str, Path)):
            with open(source, "rb") as f:
                data = f.read()
        else:
            data = source

        if len(data) < HEADER_SIZE:
            raise ValueError(f"File size {len(data)} bytes is too small for a valid .p2m2 header (min {HEADER_SIZE})")

        version = data[0]
        if version != 1:
            raise ValueError(f"Unsupported .p2m2 version: {version} (expected 1)")

        emulator_tag = data[1:51].split(b"\x00")[0].decode("utf-8", errors="replace")
        author = data[51:306].split(b"\x00")[0].decode("utf-8", errors="replace")
        game_title = data[306:561].split(b"\x00")[0].decode("utf-8", errors="replace")
        total_frames = struct.unpack_from("<I", data, 561)[0]
        undo_count = struct.unpack_from("<I", data, 565)[0]
        savestate_flag = data[569]

        header = P2M2Header(
            version=version,
            emulator_tag=emulator_tag,
            author=author,
            game_title=game_title,
            total_frames=total_frames,
            undo_count=undo_count,
            savestate_flag=savestate_flag,
            raw_header_bytes=data[:HEADER_SIZE],
        )

        payload = data[HEADER_SIZE : HEADER_SIZE + (total_frames * FRAME_PAYLOAD_SIZE)]
        return cls(header, payload)


def truncate_p2m2_file(src_path: Union[str, Path], dst_path: Union[str, Path], target_frames: int) -> int:
    """
    Truncate a .p2m2 file to target_frames and write to dst_path.
    Returns the total bytes written (606 + target_frames * 36).
    """
    replay = P2M2Replay.load(src_path)
    truncated = replay.truncate(target_frames)
    return truncated.write(dst_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse and manipulate PCSX2 .p2m2 replay files.")
    parser.add_argument("replay", type=str, help="Path to .p2m2 replay file")
    parser.add_argument("--info", action="store_true", help="Display replay header info and frame count")
    parser.add_argument("--truncate", type=int, default=None, help="Truncate replay to N frames")
    parser.add_argument("--output", type=str, default=None, help="Output path for truncated replay")
    parser.add_argument("--dump-frame", type=int, default=None, help="Dump decoded inputs for frame N")
    args = parser.parse_args()

    replay_path = Path(args.replay)
    if not replay_path.exists():
        print(f"Error: Replay file not found: {replay_path}", file=sys.stderr)
        return 1

    replay = P2M2Replay.load(replay_path)

    if args.info or (args.truncate is None and args.dump_frame is None):
        print(f"File:           {replay_path}")
        print(f"Version:        {replay.header.version}")
        print(f"Emulator Tag:   {replay.header.emulator_tag}")
        print(f"Author:         {replay.header.author}")
        print(f"Game Title:     {replay.header.game_title}")
        print(f"Total Frames:   {replay.header.total_frames} (~{replay.header.total_frames / 60.0:.2f} s)")
        print(f"Payload Size:   {len(replay.raw_payload)} bytes")

    if args.dump_frame is not None:
        frame = replay.get_frame(args.dump_frame)
        print(f"\n--- Frame {frame.frame_index} ---")
        print(f"  P1 Buttons: 0x{frame.port0.buttons:04X} ({', '.join(frame.port0.pressed_button_names) or 'None'})")
        print(f"  P1 Sticks:  LX={frame.port0.lx} LY={frame.port0.ly} RX={frame.port0.rx} RY={frame.port0.ry}")
        print(f"  P2 Buttons: 0x{frame.port1.buttons:04X} ({', '.join(frame.port1.pressed_button_names) or 'None'})")

    if args.truncate is not None:
        if not args.output:
            print("Error: --output required when using --truncate", file=sys.stderr)
            return 1
        out_bytes = truncate_p2m2_file(replay_path, args.output, args.truncate)
        print(f"Truncated replay written to {args.output} ({args.truncate} frames, {out_bytes} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
