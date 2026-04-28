#!/usr/bin/env python3
"""
Lint the wiki/ tree.

Checks:
  - Broken [[wiki-links]] (target page does not exist)
  - Missing required frontmatter fields
  - Basename collisions across the whole wiki/ tree
  - Stub debt (pages with status: stub older than --stub-days)
  - Orphaned pages (page exists in wiki/ but not referenced in index.md)
  - Unresolved CONTRADICTION: blocks (warnings)

Exit code: 1 if any errors, 0 if only warnings (or clean). CI-friendly.

Stdlib only.
"""

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
INDEX_PATH = WIKI_DIR / "index.md"
LOG_PATH = WIKI_DIR / "log.md"

REQUIRED_FRONTMATTER = [
    "type",
    "name",
    "status",
    "owner",
    "sources",
    "source_hashes",
    "tags",
    "last_updated",
]

VALID_STATUSES = {"stub", "draft", "reviewed"}

WIKILINK_RE = re.compile(r"\[\[([^\[\]\|]+?)(?:\|[^\[\]]*)?\]\]")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text):
    """
    Minimal YAML-ish frontmatter parser. Handles the shapes used in this wiki:
      - scalar:           key: value
      - inline list:      key: [a, b, c]
      - block list:       key:\n  - a\n  - b
      - inline map:       key: {}
      - block map:        key:\n  path/to/file: <hash>

    Returns (data dict, raw frontmatter string) or (None, None) if no frontmatter.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, None
    raw = m.group(1)
    lines = raw.split("\n")

    data = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        # Top-level key (no leading indent).
        if line.startswith(" ") or line.startswith("\t"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if value == "":
            # Could be a block list or block map. Peek ahead.
            block_lines = []
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() == "":
                    block_lines.append(nxt)
                    j += 1
                    continue
                if nxt.startswith(" ") or nxt.startswith("\t"):
                    block_lines.append(nxt)
                    j += 1
                else:
                    break
            data[key] = parse_block(block_lines)
            i = j
            continue

        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if inner == "":
                data[key] = []
            else:
                data[key] = [item.strip().strip('"').strip("'") for item in inner.split(",")]
        elif value.startswith("{") and value.endswith("}"):
            inner = value[1:-1].strip()
            if inner == "":
                data[key] = {}
            else:
                # Single-line inline map; rare here but handle simple "k: v, k: v".
                d = {}
                for pair in inner.split(","):
                    if ":" in pair:
                        pk, _, pv = pair.partition(":")
                        d[pk.strip().strip('"').strip("'")] = pv.strip().strip('"').strip("'")
                data[key] = d
        else:
            data[key] = value.strip().strip('"').strip("'")
        i += 1
    return data, raw


def parse_block(block_lines):
    """Block under a key with empty value: list (- items) or map (k: v)."""
    non_empty = [ln for ln in block_lines if ln.strip()]
    if not non_empty:
        return []
    # If every non-empty line starts (after indent) with "-", it's a list.
    is_list = all(ln.lstrip().startswith("- ") or ln.lstrip() == "-" for ln in non_empty)
    if is_list:
        out = []
        for ln in non_empty:
            item = ln.lstrip()[1:].strip()
            out.append(item.strip('"').strip("'"))
        return out
    # Otherwise treat as a map.
    out = {}
    for ln in non_empty:
        s = ln.strip()
        if ":" not in s:
            continue
        k, _, v = s.partition(":")
        out[k.strip().strip('"').strip("'")] = v.strip().strip('"').strip("'")
    return out


def collect_wiki_pages():
    """Return list of Path objects for every .md under wiki/, excluding index.md and log.md."""
    pages = []
    for p in WIKI_DIR.rglob("*.md"):
        if p.name in ("index.md", "log.md"):
            continue
        pages.append(p)
    return pages


def parse_iso_date(s):
    if not s or not isinstance(s, str):
        return None
    s = s.strip().strip('"').strip("'")
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def main():
    ap = argparse.ArgumentParser(description="Lint the Incident & Postmortem Wiki.")
    ap.add_argument(
        "--stub-days",
        type=int,
        default=30,
        help="Stub pages older than this many days are flagged as warnings (default: 30).",
    )
    ap.add_argument(
        "--today",
        default=None,
        help="Override today's date (YYYY-MM-DD), useful for tests.",
    )
    args = ap.parse_args()

    today = parse_iso_date(args.today) if args.today else date.today()

    if not WIKI_DIR.is_dir():
        print(f"ERROR: wiki/ directory not found at {WIKI_DIR}", file=sys.stderr)
        return 1

    errors = []
    warnings = []

    pages = collect_wiki_pages()
    page_basenames = {p.stem: p for p in pages}

    # 1. Basename collisions across the whole wiki/ tree.
    seen = {}
    for p in pages:
        seen.setdefault(p.stem, []).append(p)
    for stem, paths in seen.items():
        if len(paths) > 1:
            rels = ", ".join(str(pp.relative_to(REPO_ROOT)) for pp in paths)
            errors.append(f"basename collision: {stem!r} appears in {rels}")

    # 2. Per-page checks: frontmatter, wiki-links, status, contradictions.
    for p in pages:
        text = p.read_text(encoding="utf-8")
        rel = p.relative_to(REPO_ROOT)
        data, _ = parse_frontmatter(text)
        if data is None:
            errors.append(f"{rel}: missing YAML frontmatter")
            continue

        for field in REQUIRED_FRONTMATTER:
            if field not in data:
                errors.append(f"{rel}: missing required frontmatter field {field!r}")

        status = data.get("status")
        if status and status not in VALID_STATUSES:
            errors.append(
                f"{rel}: invalid status {status!r} (must be one of {sorted(VALID_STATUSES)})"
            )

        # Stub debt — warning only.
        if status == "stub":
            lu = parse_iso_date(data.get("last_updated"))
            if lu is None:
                warnings.append(f"{rel}: stub with unparseable last_updated")
            else:
                age = (today - lu).days
                if age > args.stub_days:
                    warnings.append(
                        f"{rel}: stub debt — last_updated {lu.isoformat()} is {age} days old"
                        f" (threshold {args.stub_days})"
                    )

        # Wiki-link targets.
        # Strip frontmatter before scanning so list items in YAML aren't double-counted.
        body = FRONTMATTER_RE.sub("", text, count=1)
        for m in WIKILINK_RE.finditer(body):
            target = m.group(1).strip()
            if "/" in target or target.endswith(".md"):
                target = target.split("/")[-1]
                if target.endswith(".md"):
                    target = target[:-3]
            if target not in page_basenames and target != p.stem:
                errors.append(f"{rel}: broken wiki-link [[{target}]]")

        # Contradictions — warning only.
        if "CONTRADICTION:" in text:
            # Pull the first line of each contradiction block for the summary.
            for line in text.splitlines():
                s = line.strip()
                if s.startswith("CONTRADICTION:"):
                    summary = s[len("CONTRADICTION:") :].strip()
                    summary = summary[:100] + ("…" if len(summary) > 100 else "")
                    warnings.append(f"{rel}: open CONTRADICTION — {summary}")

    # 3. Orphans — every page must be referenced (by basename wiki-link) from index.md.
    if INDEX_PATH.is_file():
        index_text = INDEX_PATH.read_text(encoding="utf-8")
        index_targets = set()
        for m in WIKILINK_RE.finditer(index_text):
            t = m.group(1).strip()
            if "/" in t or t.endswith(".md"):
                t = t.split("/")[-1]
                if t.endswith(".md"):
                    t = t[:-3]
            index_targets.add(t)
        for p in pages:
            if p.stem not in index_targets:
                errors.append(f"{p.relative_to(REPO_ROOT)}: orphaned (not linked from wiki/index.md)")
    else:
        errors.append("wiki/index.md is missing")

    # Report.
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)

    print()
    print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s), {len(pages)} page(s) scanned.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
