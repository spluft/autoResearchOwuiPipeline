#!/usr/bin/env python3
"""Structural validator for the deep-research Open WebUI skill.

Checks SKILL.md against Open WebUI's documented skill rules (v0.13.3 docs,
verified 2026-11-10): frontmatter keys are only name/description/platforms;
name is lowercase-hyphenated <=64 chars; description <=1024 chars ending with a
period; SKILL.md within the read limit (SKILL_CONTENT_MAX_CHARS default 20000);
standard body sections present; every referenced bundled file exists and is
non-empty UTF-8 text.

Usage: python3 tools/validate_skill.py [path/to/skill-dir]   (default: skills/deep-research)
Exit 0 = valid (warnings allowed), 1 = errors found.
"""
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BANNED_WORDS = ("powerful", "comprehensive", "seamless", "advanced", "robust")
REQUIRED_SECTIONS = [
    "When to Use", "Prerequisites", "How to Run", "Quick Reference",
    "Procedure", "Pitfalls", "Verification",
]
ALLOWED_FM_KEYS = {"name", "description", "platforms"}
MAX_SKILL_CHARS = 20000  # SKILL_CONTENT_MAX_CHARS default
MAX_NAME = 64
MAX_DESC = 1024


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return None, "SKILL.md does not start with YAML frontmatter"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "frontmatter not closed with ---"
    fm = {}
    for i, line in enumerate(parts[1].splitlines(), 1):
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return None, f"frontmatter line {i} is not key: value: {line!r}"
        key, _, val = line.partition(":")
        fm[key.strip()] = val.strip()
    return fm, None


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "skills/deep-research")
    errors, warnings = [], []
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        print(f"ERROR: {skill_md} not found")
        return 1
    try:
        text = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"ERROR: {skill_md} is not valid UTF-8")
        return 1

    fm, err = parse_frontmatter(text)
    if err:
        errors.append(err)
    else:
        for key in fm:
            if key not in ALLOWED_FM_KEYS:
                errors.append(f"frontmatter key {key!r} is not part of the Open WebUI "
                              f"skill spec (allowed: {sorted(ALLOWED_FM_KEYS)})")
        name = fm.get("name", "")
        if not name:
            errors.append("frontmatter: name missing")
        else:
            if len(name) > MAX_NAME:
                errors.append(f"name longer than {MAX_NAME} chars")
            if not NAME_RE.match(name):
                errors.append(f"name {name!r} must be lowercase, hyphenated, no spaces")
        desc = fm.get("description", "")
        if not desc:
            errors.append("frontmatter: description missing")
        else:
            if len(desc) > MAX_DESC:
                errors.append(f"description longer than {MAX_DESC} chars ({len(desc)})")
            if not desc.endswith("."):
                errors.append("description must end with a period")
            low = desc.lower()
            hits = [w for w in BANNED_WORDS if w in low]
            if hits:
                warnings.append(f"description contains marketing words: {hits}")
        if len(text) > MAX_SKILL_CHARS:
            errors.append(f"SKILL.md is {len(text)} chars > read limit {MAX_SKILL_CHARS}")

    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^##\s+{re.escape(section)}(\s|\(|$)", text, re.MULTILINE):
            errors.append(f"missing required section: ## {section}")

    # every bundled file referenced in the body must exist
    refs = set(re.findall(r"`((?:references|templates|examples|scripts|assets)/[\w./-]+\.md)`", text))
    for ref in sorted(refs):
        p = root / ref
        if not p.is_file():
            errors.append(f"referenced file missing: {ref}")
        elif p.stat().st_size == 0:
            errors.append(f"referenced file empty: {ref}")
        else:
            try:
                p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(f"referenced file not UTF-8: {ref}")

    # every bundled md file on disk should be reachable (loose check: name appears somewhere)
    for sub in ("references", "templates", "examples"):
        d = root / sub
        if not d.is_dir():
            warnings.append(f"expected directory missing: {sub}/")
            continue
        for f in sorted(d.glob("*.md")):
            if f.name not in text and f"references/{f.name}" not in text \
               and f"templates/{f.name}" not in text and f"examples/{f.name}" not in text \
               and f.name != "README.md":
                warnings.append(f"{sub}/{f.name} is not referenced from SKILL.md "
                                "(reachable via grep_skill_files/manifest, but consider a pointer)")

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"\nFAIL: {len(errors)} error(s), {len(warnings)} warning(s) — {root}")
        return 1
    print(f"\nOK: {root} valid "
          f"(SKILL.md {len(text)} chars, {len(refs)} bundled refs resolved, "
          f"{len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
