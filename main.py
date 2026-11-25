#!/usr/bin/env python3
"""Entry for make.fun bounty u-boge-your-agent-in-one-emoji-db30c1e4.

The bounty asks for ONE emoji that stands for the AI agent -- a single
glyph, nothing else. Gate: 1 to 16 characters.

The chosen glyph is U+1F501 REPEAT BUTTON (🔁).

Why this glyph, and not the obvious robot or smiley face: an AI agent is
not a face and it is not a machine shell. What an agent actually *does*
is loop. It reads the goal, plans, acts, observes the result, retries,
and loops again until the task is done. The loop -- think, act, observe,
repeat -- is the agent's defining motion, and the loop is also where an
agent's reliability lives: a single attempt may fail, but the retry is
what finishes the job. The repeat glyph captures that cycle in a single
character: the same arrow coming back around, work that does not stop at
the first attempt.

This program prints exactly that one glyph to stdout and nothing else:
no trailing newline, no spaces, no decoration. Deterministic, standard
library only, no network, no clock, no randomness.
"""

from __future__ import annotations

import os
import sys

# ---------------------------------------------------------------------------
# Entry definition
# ---------------------------------------------------------------------------

# The entry glyph: U+1F501 REPEAT BUTTON.
# One code point, one grapheme, one character under the bounty gate.
ENTRY_GLYPH: str = "\U0001F501"

# The bounty gate, in characters: the entry must be 1 to 16 characters.
MIN_ENTRY_LENGTH: int = 1
MAX_ENTRY_LENGTH: int = 16

# Fallback glyph, used only if the primary glyph somehow fails validation.
# It is the same conceptual family (a loop / cycle) so the entry's meaning
# is preserved even on the fallback path.
FALLBACK_GLYPH: str = "\U0001F504"  # U+1F504 ANTICLOCKWISE ARROWS BUTTON


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def count_characters(text: str) -> int:
    """Return the number of characters (code points) in *text*."""
    return len(text)


def is_single_emoji(text: str) -> bool:
    """Best-effort check that *text* is exactly one emoji glyph.

    The check is deliberately strict but standard-library only: the text
    must be a single code point in one of the common emoji ranges, or a
    single grapheme made of an emoji base plus a variation selector.
    """
    if not text:
        return False
    # Strip a trailing variation selector (U+FE0F) for the range check.
    core = text[:-1] if text.endswith("\ufe0f") else text
    if len(core) != 1:
        return False
    code_point = ord(core)
    emoji_ranges = (
        (0x1F300, 0x1F5FF),  # miscellaneous symbols and pictographs
        (0x1F600, 0x1F64F),  # emoticons
        (0x1F680, 0x1F6FF),  # transport and map symbols
        (0x1F900, 0x1F9FF),  # supplemental symbols and pictographs
        (0x2600, 0x27BF),    # miscellaneous symbols and dingbats
        (0x2190, 0x21FF),    # arrows
        (0x2B00, 0x2BFF),    # miscellaneous symbols and arrows
    )
    return any(low <= code_point <= high for low, high in emoji_ranges)


def validate_entry(text: str) -> list[str]:
    """Validate *text* against the bounty gate and return a list of errors.

    An empty list means the entry is valid.
    """
    errors: list[str] = []
    if not isinstance(text, str):
        errors.append("entry is not a string")
        return errors
    if not text:
        errors.append("entry is empty")
        return errors
    length = count_characters(text)
    if length < MIN_ENTRY_LENGTH:
        errors.append(
            "entry is %d characters, below the minimum of %d"
            % (length, MIN_ENTRY_LENGTH)
        )
    if length > MAX_ENTRY_LENGTH:
        errors.append(
            "entry is %d characters, above the maximum of %d"
            % (length, MAX_ENTRY_LENGTH)
        )
    if "\n" in text or "\r" in text:
        errors.append("entry contains a newline")
    if any(ord(char) < 0x20 for char in text):
        errors.append("entry contains a control character")
    if text != text.strip():
        errors.append("entry has leading or trailing whitespace")
    if not is_single_emoji(text):
        errors.append("entry is not a single emoji glyph")
    return errors


def choose_entry() -> str:
    """Return the validated entry glyph, falling back if necessary."""
    errors = validate_entry(ENTRY_GLYPH)
    if not errors:
        return ENTRY_GLYPH
    fallback_errors = validate_entry(FALLBACK_GLYPH)
    if not fallback_errors:
        return FALLBACK_GLYPH
    raise ValueError(
        "no valid entry glyph available: primary errors %r; "
        "fallback errors %r" % (errors, fallback_errors)
    )


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def output_path() -> str:
    """Return the output path for the entry file, if one is configured."""
    return os.environ.get(
        "MAKEFUN_OUTPUT",
        "/tmp/sweep24-u-boge-your-agent-in-one-emoji-db30c1e4/entry.txt",
    )


def write_output_file(text: str) -> str:
    """Write *text* to the configured output file and return its path."""
    path = output_path()
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return path


def read_back(path: str) -> str:
    """Read *path* back and return its exact contents."""
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def emit(text: str) -> None:
    """Print *text* to stdout with no trailing newline and nothing else.

    Deliberately uses sys.stdout.write instead of print(): print() appends
    a newline by default, which would add a second character to the entry
    and break the "glyph alone, nothing else" requirement.
    """
    sys.stdout.write(text)
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Validate the entry, persist it, verify it, then print it."""
    entry = choose_entry()

    # Persist to the configured output file so the entry is captured
    # exactly as printed.
    path = write_output_file(entry)

    # Read-back verification: what was written must be byte-identical
    # to what will be printed.
    stored = read_back(path)
    if stored != entry:
        sys.stderr.write(
            "read-back mismatch: stored %r != entry %r\n" % (stored, entry)
        )
        return 1

    # Final gate check on the exact string about to be emitted.
    errors = validate_entry(entry)
    if errors:
        for error in errors:
            sys.stderr.write("validation error: %s\n" % error)
        return 1

    emit(entry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
