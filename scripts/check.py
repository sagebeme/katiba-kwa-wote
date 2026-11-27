"""Check the course files for the three mistakes that matter most.

1. Every lesson has its required sections ("Kwa ufupi", "What you can do", "Where to go", "Quick quiz").
2. Every phone number or short code in the lessons and checklists also appears in WHERE-TO-GO.md,
   which is the one list of numbers checked against official websites.
3. Every relative Markdown link points to a file that exists.

Run from the repo root: python3 scripts/check.py
Exits 0 when everything passes, 1 otherwise, and prints each problem to stderr.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_SECTIONS = ("Kwa ufupi", "## What you can do", "## Where to go", "## Quick quiz")
# Phone-like tokens: "0800 720 640", "(020) 2877000", "1559", "SMS 22359". Short codes only count when
# written in bold or after "SMS"/"toll free", so years and article numbers are not mistaken for numbers.
PHONE = re.compile(r"\(?0\d{2,3}\)?[ -]?\d{3}[ -]?\d{3,4}|\+?254[\d -]{8,13}\d")
SHORT_CODE = re.compile(r"(?:\*\*|SMS\s+|[Tt]oll free\s+(?:/\s*SMS\s+)?)(\d{4,5})\b")
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


def digits(text: str) -> str:
    """Return only the digits of text, so '(020) 2877000' and '020 2877000' compare equal."""
    return re.sub(r"\D", "", text)


def numbers_in(text: str) -> set[str]:
    """Return the digit strings of every phone number and short code found in text."""
    found = {digits(m) for m in PHONE.findall(text)}
    found |= set(SHORT_CODE.findall(text))
    return found


def main() -> int:
    """Run all checks and return the process exit code."""
    problems = []
    lessons = sorted((ROOT / "lessons").glob("*.md"))
    if not lessons:
        problems.append("no lessons found in lessons/")

    for path in lessons:
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                problems.append(f"{path.relative_to(ROOT)}: missing section '{section}'")

    directory = digits((ROOT / "WHERE-TO-GO.md").read_text(encoding="utf-8"))
    for path in lessons + sorted((ROOT / "checklists").glob("*.md")):
        for number in numbers_in(path.read_text(encoding="utf-8")):
            if number not in directory:
                problems.append(f"{path.relative_to(ROOT)}: number {number} is not in WHERE-TO-GO.md")

    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).resolve().exists():
                problems.append(f"{path.relative_to(ROOT)}: broken link to {target}")

    for problem in problems:
        print(problem, file=sys.stderr)
    print("all checks passed" if not problems else f"{len(problems)} problem(s) found")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
