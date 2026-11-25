#!/usr/bin/env python3
"""The Router Confesses — entry program.

Writes one one-line excuse a home Wi-Fi router gives for dropping the
connection at the exact moment a movie reaches its climax, to
/output/entry.txt. The line must pass the gate: UTF-8 text of 1 to 200
characters, not only white space, a single line.

Usage:
    python3 main.py [--output PATH] [--self-test]
"""

import argparse
import os
import sys

ENTRY = (
    "I cut the Wi-Fi at the climax because the ending was too good to "
    "share \u2014 I am watching it right now, in 4K, alone."
)

DEFAULT_OUTPUT = "/output/entry.txt"


def validate(text):
    """Check the entry against the competition gate. Returns a list of
    problems (empty when valid)."""
    problems = []
    if not isinstance(text, str):
        return ["entry is not text"]
    if not (1 <= len(text) <= 200):
        problems.append(
            "length %d characters, must be 1-200" % len(text))
    if not text.strip():
        problems.append("entry is only white space")
    if text != text.strip():
        problems.append("leading or trailing white space")
    if "\n" in text or "\r" in text:
        problems.append("entry must be a single line")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in text):
        problems.append("entry contains control characters")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append("entry is not valid UTF-8: %s" % exc)
    return problems


def _probe(text):
    """Run validate() against a probe string; True when it is rejected."""
    return bool(validate(text))


def write_entry(path):
    problems = validate(ENTRY)
    if problems:
        for problem in problems:
            print("gate failure: %s" % problem, file=sys.stderr)
        return 1
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(ENTRY)
    # Read it back: a write that silently truncates or mangles the line
    # must fail loudly here, not pass the gate check on a stale file.
    with open(path, "r", encoding="utf-8", newline="") as handle:
        written = handle.read()
    if written != ENTRY:
        print("gate failure: wrote %r, read back %r"
              % (ENTRY, written), file=sys.stderr)
        return 1
    print(ENTRY)
    return 0


def self_test():
    """Validate the entry text and a round-trip write/read."""
    problems = validate(ENTRY)
    # Boundary probes: each of these must be rejected by the gate.
    probes = {
        "empty": "",
        "whitespace-only": "   ",
        "201 chars": "x" * 201,
        "multi-line": "line one\nline two",
        "carriage return": "one\r two",
        "leading space": " " + ENTRY,
        "trailing space": ENTRY + " ",
        "control char": ENTRY + "\x01",
        "tab": "a\tb",
    }
    for name, probe in probes.items():
        if not _probe(probe):
            problems.append("probe accepted, should reject: %s" % name)
    # Boundary passes: 1-char and 200-char inputs must be accepted.
    for name, probe in {"1 char": "x", "200 chars": "x" * 200}.items():
        if _probe(probe):
            problems.append("probe rejected, should accept: %s" % name)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        probe = os.path.join(tmp, "entry.txt")
        if write_entry(probe) != 0:
            problems.append("write failed")
        else:
            with open(probe, "rb") as handle:
                raw = handle.read()
            decoded = raw.decode("utf-8")
            if decoded != ENTRY:
                problems.append("round-trip mismatch")
            if raw.endswith(b"\n"):
                problems.append("output ends with a newline")
    if problems:
        for problem in problems:
            print("self-test FAIL: %s" % problem, file=sys.stderr)
        return 1
    print("self-test OK: %d chars, %d bytes, single line, no padding"
          % (len(ENTRY), len(ENTRY.encode("utf-8"))))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="where to write the entry (default: %(default)s)")
    parser.add_argument("--self-test", action="store_true",
                        help="validate the entry against the gate and exit")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    return write_entry(args.output)


if __name__ == "__main__":
    raise SystemExit(main())
