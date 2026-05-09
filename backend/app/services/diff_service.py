"""Contract diff service — line-level redline using stdlib difflib."""

import difflib
from typing import Literal

DiffOp = Literal["equal", "insert", "delete", "replace"]


def compute_line_diff(text_a: str, text_b: str) -> list[dict]:
    """Compute a line-level diff between two contract texts.

    Returns a list of blocks, each shaped like::

        {"op": "equal" | "insert" | "delete" | "replace",
         "a_lines": [...],
         "b_lines": [...]}

    ``a_lines`` is the slice from ``text_a``; ``b_lines`` from ``text_b``.
    Frontend renders inserts as green (added in B), deletes as red
    (removed from A), replaces as yellow (modified), equal as neutral.
    """
    a = text_a.splitlines()
    b = text_b.splitlines()
    matcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    blocks: list[dict] = []
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        blocks.append(
            {
                "op": op,
                "a_lines": a[i1:i2],
                "b_lines": b[j1:j2],
            }
        )
    return blocks


def compute_summary(blocks: list[dict]) -> dict:
    """Roll up a diff into a summary of additions/deletions/modifications."""
    added = 0
    removed = 0
    modified = 0
    unchanged = 0
    for block in blocks:
        op = block["op"]
        if op == "insert":
            added += len(block["b_lines"])
        elif op == "delete":
            removed += len(block["a_lines"])
        elif op == "replace":
            modified += max(len(block["a_lines"]), len(block["b_lines"]))
        else:
            unchanged += len(block["a_lines"])
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged,
    }
