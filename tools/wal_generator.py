"""
wal_generator.py — IBM RPA .wal file generator.

IBM RPA .wal files are protobuf binary files. Writing plain text to a .wal
extension produces a file Studio cannot open (ProtoBuf.ProtoException).

BINARY STRUCTURE (verified from template/template.wal hex dump):
┌─────────────────────────────────────────────────────────────┐
│  0x12              — protobuf field tag (field 2, wire 2)   │ PREFIX
│  <varint>          — byte-length of WAL text that follows   │
├─────────────────────────────────────────────────────────────┤
│  <WAL text bytes>  — UTF-8 command lines (editable body)    │ BODY
│  0x0D 0x0A         — CRLF after last endSub line            │
├─────────────────────────────────────────────────────────────┤
│  0x2A              — protobuf field tag (field 5, wire 2)   │ SUFFIX
│  0x08              — version sub-field prefix               │
│  <version bytes>   — e.g. "30.0.3.0"                        │
└─────────────────────────────────────────────────────────────┘

USAGE
-----
  # Generate a new .wal from a source template + plain-text script:
  python wal_generator.py --template template.wal --script my_script.wal.txt --output my_script.wal

  # In-place update an existing .wal body (keeps its own suffix):
  python wal_generator.py --template call_python.wal --script updated.wal.txt --output call_python.wal

ARGUMENTS
---------
  --template  PATH   Existing valid .wal binary — used to read the binary suffix
  --script    PATH   Plain UTF-8 .wal.txt source file — the WAL command lines to embed
  --output    PATH   Destination .wal binary file (may equal --template for in-place)
"""

import sys
import argparse
from pathlib import Path


# ── Protobuf varint codec ─────────────────────────────────────────────────────

def encode_varint(value: int) -> bytes:
    """Encode a non-negative integer as a protobuf base-128 varint."""
    if value < 0:
        raise ValueError(f"varint value must be non-negative, got {value}")
    out = []
    while True:
        byte = value & 0x7F
        value >>= 7
        out.append(byte | (0x80 if value else 0))
        if not value:
            break
    return bytes(out)


def decode_varint(data: bytes, pos: int) -> tuple[int, int]:
    """Decode a protobuf varint from data[pos:]. Returns (value, next_pos)."""
    result, shift = 0, 0
    while True:
        if pos >= len(data):
            raise ValueError("Buffer ended while reading varint")
        b = data[pos]; pos += 1
        result |= (b & 0x7F) << shift
        shift += 7
        if not (b & 0x80):
            return result, pos


# ── .wal parser ───────────────────────────────────────────────────────────────

WAL_TEXT_TAG = 0x12   # protobuf field 2, wire type 2
VERSION_TAG  = 0x2A   # protobuf field 5, wire type 2


def parse_wal(data: bytes) -> tuple[bytes, bytes]:
    """
    Parse a .wal binary into (body_bytes, suffix_bytes).

    body_bytes   — the raw WAL text content (UTF-8)
    suffix_bytes — everything from the 0x2A version tag to EOF (appended verbatim)

    Raises ValueError if the file does not start with the expected 0x12 tag.
    """
    pos = 0
    if not data or data[pos] != WAL_TEXT_TAG:
        raise ValueError(
            f"First byte is 0x{data[0]:02X if data else 'empty'}, expected 0x12. "
            "File may not be a valid IBM RPA .wal binary."
        )
    pos += 1

    text_len, pos = decode_varint(data, pos)
    body = data[pos : pos + text_len]
    suffix = data[pos + text_len :]

    return body, suffix


# ── .wal writer ───────────────────────────────────────────────────────────────

def build_wal(script_text: str, suffix: bytes) -> bytes:
    """
    Assemble a .wal binary from plain script text + the original binary suffix.

    The script text is encoded as UTF-8. Line endings are normalised to CRLF
    (IBM RPA Studio stores \r\n internally). The protobuf length varint is
    recalculated for the new content length.
    """
    # Normalise to CRLF
    normalised = script_text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
    body = normalised.encode("utf-8")

    return bytes([WAL_TEXT_TAG]) + encode_varint(len(body)) + body + suffix


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate or update an IBM RPA .wal binary from plain WAL text source."
    )
    parser.add_argument("--template", required=True,
                        help="Existing valid .wal binary (source of the binary suffix).")
    parser.add_argument("--script",   required=True,
                        help="Plain UTF-8 .wal.txt file containing WAL command lines.")
    parser.add_argument("--output",   required=True,
                        help="Output .wal binary path (may equal --template for in-place update).")
    args = parser.parse_args()

    template_path = Path(args.template)
    script_path   = Path(args.script)
    output_path   = Path(args.output)

    # ── Read template binary ──────────────────────────────────────────────────
    raw = template_path.read_bytes()
    try:
        original_body, suffix = parse_wal(raw)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Template : {template_path} ({len(raw)} bytes, body={len(original_body)} bytes)")
    print(f"Suffix   : {suffix.hex(' ')}")

    # ── Read new WAL script text ──────────────────────────────────────────────
    script_text = script_path.read_text(encoding="utf-8")
    print(f"Script   : {script_path} ({len(script_text)} chars)")

    # ── Build new binary ──────────────────────────────────────────────────────
    new_data = build_wal(script_text, suffix)
    output_path.write_bytes(new_data)

    body_size = len(new_data) - 1 - len(encode_varint(len(new_data))) - len(suffix)
    print(f"Output   : {output_path} ({len(new_data)} bytes)")
    print("Done — binary suffix preserved, body replaced.")


if __name__ == "__main__":
    main()
