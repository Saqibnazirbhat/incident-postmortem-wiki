#!/usr/bin/env python3
"""
Check (and optionally update) source_hashes: in every wiki page's frontmatter.

For every page under wiki/ with a `source_hashes:` block in its YAML frontmatter,
compute the SHA-256 of each referenced raw/ source file and compare against the
recorded hash. Report missing files, mismatches, or files referenced but not yet
hashed.

  python tools/check-drift.py            # report only; non-zero exit on drift
  python tools/check-drift.py --update   # rewrite the source_hashes block in place

Stdlib only: hashlib, pathlib, re, sys, argparse.
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = REPO_ROOT / "wiki"

FRONTMATTER_RE = re.compile(r"\A(---\s*\n)(.*?)(\n---\s*\n)", re.DOTALL)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_sources_list(frontmatter):
    """Return list of source paths from `sources:` (inline or block list)."""
    sources = []
    lines = frontmatter.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^sources\s*:", line):
            _, _, rest = line.partition(":")
            rest = rest.strip()
            if rest.startswith("[") and rest.endswith("]"):
                inner = rest[1:-1].strip()
                if inner:
                    sources = [
                        s.strip().strip('"').strip("'") for s in inner.split(",") if s.strip()
                    ]
                return sources
            if rest == "":
                # Block list follows.
                j = i + 1
                while j < len(lines):
                    nxt = lines[j]
                    if nxt.strip() == "":
                        j += 1
                        continue
                    if not (nxt.startswith(" ") or nxt.startswith("\t")):
                        break
                    s = nxt.strip()
                    if s.startswith("-"):
                        sources.append(s[1:].strip().strip('"').strip("'"))
                    j += 1
                return sources
        i += 1
    return sources


def find_source_hashes_block(frontmatter):
    """
    Locate the `source_hashes:` block in the frontmatter.

    Returns (start_line, end_line, indent, parsed_map) where start_line is the
    index of the `source_hashes:` line and end_line is one past the last line of
    the block (so frontmatter[start:end] covers the whole block to replace).
    Returns None if there is no source_hashes key.
    """
    lines = frontmatter.split("\n")
    for i, line in enumerate(lines):
        if re.match(r"^source_hashes\s*:", line):
            _, _, rest = line.partition(":")
            rest = rest.strip()
            if rest.startswith("{") and rest.endswith("}"):
                # Inline map (likely empty: {}).
                return (i, i + 1, "  ", {})
            if rest != "":
                # Inline value but not a map. Treat as empty + replace whole line.
                return (i, i + 1, "  ", {})
            # Block map. Capture indented lines.
            j = i + 1
            mapping = {}
            indent = "  "
            block_end = j
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() == "":
                    j += 1
                    continue
                if not (nxt.startswith(" ") or nxt.startswith("\t")):
                    break
                # Capture indent from first content line.
                lead = re.match(r"^(\s+)", nxt).group(1)
                indent = lead
                s = nxt.strip()
                if ":" in s:
                    k, _, v = s.partition(":")
                    mapping[k.strip().strip('"').strip("'")] = v.strip().strip('"').strip("'")
                j += 1
                block_end = j
            return (i, block_end, indent, mapping)
    return None


def render_block(indent, mapping):
    """Render `source_hashes:` block lines using a known indent."""
    lines = ["source_hashes:"]
    if not mapping:
        # Use the inline empty form for cleanliness.
        return ["source_hashes: {}"]
    for k in mapping:
        lines.append(f"{indent}{k}: {mapping[k]}")
    return lines


def process_page(page_path, update=False):
    """
    Returns (had_drift, messages). had_drift is True when at least one source's
    hash is missing, mismatched, or its file is missing. In --update mode the
    file is rewritten with current hashes (which makes had_drift False going
    forward).
    """
    text = page_path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return False, []
    fm_open, fm_body, fm_close = m.group(1), m.group(2), m.group(3)
    rest = text[m.end() :]
    rel = page_path.relative_to(REPO_ROOT)

    sources = parse_sources_list(fm_body)
    hashes_block = find_source_hashes_block(fm_body)
    recorded = hashes_block[3] if hashes_block else {}

    messages = []
    drift = False
    new_hashes = {}

    for src in sources:
        src_path = REPO_ROOT / src
        if not src_path.is_file():
            messages.append(f"{rel}: source missing on disk: {src}")
            drift = True
            # Preserve any old recorded hash to avoid losing history.
            if src in recorded:
                new_hashes[src] = recorded[src]
            continue
        actual = sha256_file(src_path)
        new_hashes[src] = actual
        if src not in recorded:
            messages.append(f"{rel}: source not yet hashed: {src}")
            drift = True
        elif recorded[src] != actual:
            messages.append(
                f"{rel}: hash mismatch for {src}\n"
                f"    recorded: {recorded[src]}\n"
                f"    actual:   {actual}"
            )
            drift = True

    # Catch sources recorded in source_hashes but no longer in `sources:`.
    for src in recorded:
        if src not in sources:
            messages.append(f"{rel}: stale entry in source_hashes (not in sources): {src}")
            drift = True

    if update and hashes_block is not None:
        start_line, end_line, indent, _ = hashes_block
        fm_lines = fm_body.split("\n")
        replacement = render_block(indent, new_hashes)
        new_fm_lines = fm_lines[:start_line] + replacement + fm_lines[end_line:]
        new_fm = "\n".join(new_fm_lines)
        new_text = fm_open + new_fm + fm_close + rest
        if new_text != text:
            page_path.write_text(new_text, encoding="utf-8")
            messages.append(f"{rel}: updated source_hashes")

    return drift, messages


def main():
    ap = argparse.ArgumentParser(
        description="Check SHA-256 drift between wiki frontmatter and raw/ sources."
    )
    ap.add_argument(
        "--update",
        action="store_true",
        help="Rewrite source_hashes blocks in place with the current hashes.",
    )
    args = ap.parse_args()

    if not WIKI_DIR.is_dir():
        print(f"ERROR: wiki/ directory not found at {WIKI_DIR}", file=sys.stderr)
        return 1

    any_drift = False
    pages_scanned = 0
    for p in sorted(WIKI_DIR.rglob("*.md")):
        if p.name in ("index.md", "log.md"):
            continue
        pages_scanned += 1
        drift, messages = process_page(p, update=args.update)
        for msg in messages:
            print(msg)
        if drift:
            any_drift = True

    print()
    if args.update:
        print(f"Update complete. {pages_scanned} page(s) scanned.")
        return 0
    print(
        f"{pages_scanned} page(s) scanned. "
        f"{'Drift detected.' if any_drift else 'No drift.'}"
    )
    return 1 if any_drift else 0


if __name__ == "__main__":
    sys.exit(main())
