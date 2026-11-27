"""Build the GitHub Pages site in docs/ from the course's Markdown files.

The Markdown files stay the single source of truth: lessons, the directory, the glossary, the checklist and the
sources are converted here, and only the home page's own sections are written in this file.

Run from the repo root: python3 site/build.py   (needs the `markdown` package, version 3)
Writes docs/ from scratch on every run.
"""

import html
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT = ROOT / "docs"
REPO_URL = "https://github.com/sagebeme/katiba-kwa-wote"
CHECKED = "27 November 2026"

# Source Markdown file -> output page, relative to docs/.
PAGES = {
    "WHERE-TO-GO.md": "where-to-go.html",
    "GLOSSARY.md": "glossary.html",
    "checklists/election-2027-checklist.md": "checklist.html",
    "SOURCES.md": "sources.html",
    "README.md": "index.html",
    "LICENSE": REPO_URL + "/blob/main/LICENSE",
}

# One illustration per lesson, from the author’s video series, with the alt text describing what it shows.
LESSON_ART = {
    "01": ("02_constitution-on-desk", "A green copy of the Constitution of Kenya, 2010, lying on a desk."),
    "02": ("05_kicc-queue", "A long queue of people waiting beside a tall building."),
    "03": ("18_rally-note", "A crowd at a rally with flags, and one hand passing a folded note to another."),
    "04": ("02_2007-ballot-box", "A ballot box with a crack running down its side, under a dark cloud."),
    "05": ("04_harambee-house-steps", "The steps of a government building with columns and a Kenyan flag."),
    "06": ("17_market-gate-dawn", "Two figures at a market gate at dawn: a trader and a county askari."),
    "07": ("22_akinyi-stall", "A trader standing behind her market stall of tomatoes."),
    "08": ("06_courthouse", "The front of a courthouse with columns and wide steps."),
}

NAV = [("Lessons", "index.html#lessons"), ("Where to go", "where-to-go.html"), ("Glossary", "glossary.html"),
       ("Checklist", "checklist.html")]

CITE_OPENERS = ("(Art ", "(Arts ", "(Election Offences Act", "(Elections Act", "(County Governments Act",
                "(s.", "(section ")


def lessons() -> list[dict]:
    """Return the lessons in order, each with its number, title, minutes, source path and output path."""
    found = []
    for path in sorted((ROOT / "lessons").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = re.search(r"^# Lesson \d+ · (.+)$", text, re.M).group(1).replace("'", "’")
        minutes = re.search(r"\*\*Time:\*\* about (\d+) minutes", text).group(1)
        found.append({"num": path.name[:2], "title": title, "minutes": minutes, "src": path,
                      "out": f"lessons/{path.stem}.html"})
    return found


def rel(from_page: str, to_page: str) -> str:
    """Return the link from one docs/ page to another (both given relative to docs/)."""
    if to_page.startswith("http"):
        return to_page
    depth = from_page.count("/")
    return "../" * depth + to_page


def wrap_citations(fragment: str) -> str:
    """Wrap "(Art 49(1)(f))"-style legal citations in <cite class="law">, outside tags and links."""
    out, i, n, in_link = [], 0, len(fragment), False
    while i < n:
        if fragment[i] == "<":
            end = fragment.index(">", i) + 1
            tag = fragment[i:end]
            in_link = tag.startswith("<a ") or (in_link and not tag.startswith("</a"))
            out.append(tag)
            i = end
            continue
        if not in_link and fragment[i] == "(" and fragment.startswith(CITE_OPENERS, i):
            depth, j = 0, i
            while j < n and fragment[j] != "<":
                depth += {"(": 1, ")": -1}.get(fragment[j], 0)
                j += 1
                if depth == 0:
                    out.append(f'<cite class="law">{fragment[i:j]}</cite>')
                    i = j
                    break
            else:
                out.append(fragment[i])
                i += 1
            continue
        out.append(fragment[i])
        i += 1
    return "".join(out)


def tidy(fragment: str) -> str:
    """Swap the Markdown's typographic shortcuts for the site's: no middle-dot strings, no en dashes."""
    fragment = re.sub(r"(<td>.*?</td>)", lambda m: m.group(1).replace(" · ", "<br>"), fragment, flags=re.S)
    fragment = fragment.replace(" · ", "; ")
    return re.sub(r"([\w)])–([\w(])", r"\1 to \2", fragment)


def render_markdown(src: Path, page: str, lesson_list: list[dict]) -> tuple[str, str, str, str]:
    """Convert one Markdown file to HTML for `page`.

    Returns (title, Kiswahili summary HTML or "", meta HTML or "", body HTML). Links to other course
    files are rewritten to their pages, and the "Next:" / "Back to:" footer line is dropped (the
    template draws its own).
    """
    text = src.read_text(encoding="utf-8")
    title = re.search(r"^# (.+)$", text, re.M).group(1).replace("'", "’")
    text = re.sub(r"^# .+\n", "", text, count=1, flags=re.M)
    text = re.sub(r"^\*\*(Next|Back to):\*\*.*$", "", text, flags=re.M)
    text = text.replace("<details>", '<details markdown="1">')
    body = markdown.markdown(text, extensions=["tables", "md_in_html", "sane_lists", "smarty"])

    summary = ""
    match = re.search(r"<blockquote>\s*(<p><strong>Kwa ufupi \(Kiswahili\):</strong>.*?</p>)\s*</blockquote>", body, re.S)
    if match:
        summary = match.group(1).replace("<strong>Kwa ufupi (Kiswahili):</strong> ", "")
        body = body.replace(match.group(0), "", 1)

    meta = ""
    match = re.search(r"<p><strong>Time:</strong>(.*?)</p>", body, re.S)
    if match:
        parts = [p.strip() for p in ("<strong>Time:</strong>" + match.group(1)).split(" · ")]
        items = []
        for part in parts:
            key, _, value = part.partition("</strong>")
            items.append(f"<div><dt>{re.sub('<.*?>', '', key).rstrip(':')}</dt><dd>{value.strip()}</dd></div>")
        meta = '<dl class="meta">' + "".join(items) + "</dl>"
        body = body.replace(match.group(0), "", 1)

    body = re.sub(r"^\s*<hr\s*/?>", "", body.strip())
    body = re.sub(r"<hr\s*/?>\s*$", "", body.strip())

    def fix_link(m: re.Match) -> str:
        target = m.group(1)
        if "://" in target or target.startswith(("mailto:", "#")):
            return m.group(0)
        path, _, anchor = target.partition("#")
        resolved = (src.parent / path).resolve().relative_to(ROOT).as_posix()
        lesson = next((les["out"] for les in lesson_list if les["src"].relative_to(ROOT).as_posix() == resolved), None)
        dest = lesson or PAGES.get(resolved)
        if dest is None:
            return f'href="{REPO_URL}/blob/main/{resolved}"'
        return f'href="{rel(page, dest)}{"#" + anchor if anchor else ""}"'

    body = re.sub(r'href="([^"]+)"', fix_link, body)
    body = re.sub(r'href="(https?://[^"]+)"', r'href="\1" rel="noopener"', body)
    body = re.sub(r"<li>\[ \] (.*?)</li>", r'<li class="task"><label><input type="checkbox"> <span>\1</span></label></li>',
                  body, flags=re.S)
    body = re.sub(r"<table>", '<div class="table"><table>', body).replace("</table>", "</table></div>")
    body = re.sub(r"<blockquote>", '<aside class="note">', body).replace("</blockquote>", "</aside>")
    return title, tidy(summary), tidy(meta), wrap_citations(tidy(body))


def shell(page: str, title: str, description: str, main: str, current: str = "") -> str:
    """Wrap a page's <main> in the shared document, nav and footer."""
    links = "".join(
        f'<li><a href="{rel(page, href)}"{" aria-current=page" if href == current else ""}>{label}</a></li>'
        for label, href in NAV)
    css = rel(page, "assets/site.css")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="preload" href="{rel(page, 'assets/fonts/NotoSerif-Regular.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{css}">
</head>
<body>
<a class="skip" href="#main">Skip to the content</a>
<header class="masthead">
  <nav class="container nav" aria-label="Main">
    <a class="wordmark" href="{rel(page, 'index.html')}">Katiba kwa Wote</a>
    <ul>{links}</ul>
  </nav>
</header>
<main id="main">
{main}
</main>
<footer class="colophon">
  <div class="container">
    <p class="colophon-mark"><a href="{rel(page, 'index.html')}">Katiba kwa Wote</a></p>
    <div class="colophon-grid">
      <p>A plain-language course on the Constitution of Kenya, 2010. It explains the law; it is not legal advice,
      and it takes no side in any election. Last checked {CHECKED}.</p>
      <p>Illustrations from the author’s video series on the Constitution. Text licensed
      <a href="{REPO_URL}/blob/main/LICENSE" rel="noopener">CC BY 4.0</a>. Typeset in Noto Serif
      (<a href="{rel(page, 'assets/fonts/OFL.txt')}">SIL Open Font License</a>).</p>
      <ul class="colophon-links">
        <li><a href="{rel(page, 'sources.html')}">Sources</a></li>
        <li><a href="{rel(page, 'where-to-go.html')}">Where to go</a></li>
        <li><a href="{REPO_URL}" rel="noopener">The course on GitHub</a></li>
      </ul>
    </div>
  </div>
</footer>
</body>
</html>
"""


def picture(page: str, name: str, alt: str, eager: bool = False) -> str:
    """Return a responsive <img> for one illustration (800w for phones, 1600w for wide screens)."""
    base = rel(page, f"assets/img/{name}")
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{base}-1600.webp" srcset="{base}-800.webp 800w, {base}-1600.webp 1600w" '
            f'sizes="(min-width: 60rem) 60vw, 100vw" width="1600" height="900" alt="{html.escape(alt)}" {loading}>')


def lesson_page(les: dict, all_lessons: list[dict]) -> str:
    """Build one lesson page."""
    page = les["out"]
    title, summary, meta, body = render_markdown(les["src"], page, all_lessons)
    title = title.split(" · ", 1)[1]
    idx = all_lessons.index(les)
    prev_l = all_lessons[idx - 1] if idx else None
    next_l = all_lessons[idx + 1] if idx + 1 < len(all_lessons) else None
    art, alt = LESSON_ART[les["num"]]
    steps = []
    if prev_l:
        steps.append(f'<a class="step prev" href="{rel(page, prev_l["out"])}"><span>Lesson {int(prev_l["num"])}, before this one</span>'
                     f'<strong>{prev_l["title"]}</strong></a>')
    if next_l:
        steps.append(f'<a class="step next" href="{rel(page, next_l["out"])}"><span>Lesson {int(next_l["num"])}, next</span>'
                     f'<strong>{next_l["title"]}</strong></a>')
    else:
        steps.append(f'<a class="step next" href="{rel(page, "checklist.html")}"><span>Course finished</span>'
                     f'<strong>Your 2027 election checklist</strong></a>')
    main = f"""
<article class="lesson">
  <header class="lesson-head container">
    <div class="lesson-title">
      <h1>{title}</h1>
      <p class="lesson-of">Lesson {int(les["num"])} of {len(all_lessons)}</p>
      {meta}
    </div>
    <figure class="lesson-art">{picture(page, art, alt, eager=True)}</figure>
  </header>
  <div class="sheet">
    <div class="sheet-inner">
      {f'<aside class="sw" lang="sw"><h2>Kwa ufupi</h2>{summary}</aside>' if summary else ''}
      <div class="prose">{body}</div>
    </div>
  </div>
  <nav class="container steps" aria-label="Lessons">{''.join(steps)}</nav>
</article>"""
    return shell(page, f"{title} | Katiba kwa Wote", f"Lesson {int(les['num'])} of a plain-language course on the Constitution of Kenya: {title}.", main)


def doc_page(src: str, page: str, all_lessons: list[dict]) -> str:
    """Build a reference page (directory, glossary, checklist, sources) from its Markdown."""
    title, summary, _meta, body = render_markdown(ROOT / src, page, all_lessons)
    main = f"""
<article class="doc">
  <header class="doc-head container"><h1>{title}</h1></header>
  <div class="sheet">
    <div class="sheet-inner">
      {f'<aside class="sw" lang="sw"><h2>Kwa ufupi</h2>{summary}</aside>' if summary else ''}
      <div class="prose">{body}</div>
    </div>
  </div>
</article>"""
    return shell(page, f"{title} | Katiba kwa Wote", f"{title}: part of a plain-language course on the Constitution of Kenya.", main, page)


# The finder on the home page. Every fact here is taken from the lessons and WHERE-TO-GO.md.
FINDER = [
    ("police", "The police stopped or arrested me",
     "You must be told why, you may stay silent and call a lawyer, and you must see a court within 24 hours.",
     "Art 49", "Stay calm, ask why, and note names, badge numbers and the time.",
     "IPOA, toll free 1559", "08"),
    ("vote", "Someone offered money for my vote",
     "Giving and taking a bribe for a vote are both crimes: up to KES 2 million, six years in prison, or both.",
     "Election Offences Act, s.9", "Refuse it, note who, where and when, and report it.",
     "IEBC, (020) 2877000, and the police", "03"),
    ("hate", "A leader is stirring up hatred",
     "Hate speech and incitement to violence are not protected by freedom of expression.",
     "Art 33(2)", "Don’t forward it. Take a screenshot and report it.",
     "NCIC, toll free or SMS 1547", "03"),
    ("register", "Am I registered to vote?",
     "Every adult citizen has the right to be registered, at one registration centre only.",
     "Art 38(3), 83", "Check your details at verify.iebc.or.ke with your ID number and year of birth.",
     "Your IEBC constituency office", "02"),
    ("fee", "My county raised a fee unasked",
     "County assemblies must let the public take part in their business, including fees and budgets.",
     "Art 196", "Ask for the county Finance Bill, and put your objection in writing.",
     "Your MCA and your county assembly", "07"),
    ("office", "A government office ignored me",
     "You have the right to administrative action that is fast, lawful, reasonable and fair.",
     "Art 47", "Write down what happened and when, and keep copies of what you sent.",
     "The Ombudsman, toll free 0800 221 349", "07"),
]

HOTLINES = [
    ("1547", "Hate speech", "NCIC, call or SMS"),
    ("1551", "Corruption", "EACC"),
    ("1559", "Police abuse", "IPOA, 24 hours"),
    ("22359", "Rights violated", "KNCHR, by SMS"),
    ("0800 720 640", "Free legal help", "Legal Aid Service"),
    ("020 2877000", "Voter registration", "IEBC"),
]

BALLOTS = [
    ("President", "Proposes national taxes and signs them into law."),
    ("Governor", "Runs county clinics, roads and markets."),
    ("Senator", "Shares money among the 47 counties."),
    ("Woman Member", "Votes on every national tax."),
    ("MP", "Votes on every national tax and the budget."),
    ("MCA", "Votes on your market fee and permit."),
]


def home(all_lessons: list[dict]) -> str:
    """Build the home page."""
    page = "index.html"
    tabs = "".join(
        f'<li><button type="button" class="finder-tab" id="tab-{key}" aria-controls="ans-{key}" aria-pressed="false">{label}</button></li>'
        for key, label, *_ in FINDER)
    panels = "".join(f"""
      <section class="finder-answer" id="ans-{key}" aria-labelledby="tab-{key}">
        <h3>{label}</h3>
        <p class="finder-law">{law} <cite class="law">({cite})</cite></p>
        <dl>
          <div><dt>Do this</dt><dd>{do}</dd></div>
          <div><dt>Go to</dt><dd>{where}</dd></div>
        </dl>
        <a class="finder-more" href="{rel(page, next(les['out'] for les in all_lessons if les['num'] == lesson))}">Read lesson {int(lesson)}</a>
      </section>""" for key, label, law, cite, do, where, lesson in FINDER)
    rows = "".join(f"""
        <li><a href="{rel(page, les['out'])}">
          <span class="row-num">{int(les['num'])}</span>
          <span class="row-title">{les['title']}</span>
          <span class="row-meta">{les['minutes']} minutes</span>
        </a></li>""" for les in all_lessons)
    ballots = "".join(f'<li class="ballot ballot-{i}"><strong>{name}</strong><span>{job}</span></li>'
                      for i, (name, job) in enumerate(BALLOTS, 1))
    hotlines = "".join(f'<li><span class="hot-num">{num}</span><span class="hot-what">{what}</span><span class="hot-who">{who}</span></li>'
                       for num, what, who in HOTLINES)
    main = f"""
<section class="hero container">
  <div class="hero-text">
    <h1>Your Constitution, in plain words.</h1>
    <p class="lede">Eight short lessons before Kenya votes on 10 August 2027.</p>
    <p class="hero-actions"><a class="button" href="{rel(page, all_lessons[0]['out'])}">Start lesson 1</a>
    <a class="quiet-link" href="#help">I need help right now</a></p>
  </div>
  <figure class="hero-art">
    {picture(page, "01_otieno-roadside", "At night, under a street lamp, a police officer stops a man walking home.", eager=True)}
    <figcaption>Otieno, stopped on his way home. He has rights here; the course starts with which ones.</figcaption>
  </figure>
</section>

<section class="finder" id="help" aria-labelledby="finder-h">
  <div class="sheet-band">
    <div class="container finder-grid">
      <div class="finder-ask">
        <h2 id="finder-h">What’s happening to you?</h2>
        <ul class="finder-tabs" role="list">{tabs}</ul>
      </div>
      <div class="finder-answers">{panels}
      </div>
    </div>
  </div>
</section>

<section class="contents container" id="lessons" aria-labelledby="lessons-h">
  <h2 id="lessons-h">Eight lessons, about ten minutes each.</h2>
  <ol class="rows">{rows}
  </ol>
</section>

<section class="ballots" aria-labelledby="ballots-h">
  <div class="container ballots-grid">
    <div class="ballots-text">
      <h2 id="ballots-h">Six ballots. The smallest one sets your market fee.</h2>
      <ol class="ballot-stack">{ballots}</ol>
      <a class="quiet-link" href="{rel(page, all_lessons[5]['out'])}">Who does what: lesson 6</a>
    </div>
    <figure class="ballots-art">
      {picture(page, "17_market-gate-dawn", "At dawn, a trader pays the market gate fee to a county askari.")}
      <figcaption>Akinyi pays the county four times before lunch.</figcaption>
    </figure>
  </div>
</section>

<section class="hotlines container" aria-labelledby="hot-h">
  <h2 id="hot-h">Six numbers worth saving in your phone.</h2>
  <ul class="hot-list">{hotlines}</ul>
  <p class="hot-note">Copied from each office’s own website on {CHECKED}. <a href="{rel(page, 'where-to-go.html')}">Every office, with addresses</a></p>
</section>

<section class="checked" aria-labelledby="checked-h">
  <div class="sheet-band">
    <div class="container checked-grid">
      <h2 id="checked-h">Every rule points to its Article.</h2>
      <blockquote class="specimen"><p>You must be brought before a court within 24 hours of arrest <cite class="law">(Art 49(1)(f))</cite>.</p></blockquote>
      <ul class="checked-list">
        <li>Each Article was checked against the official text on Kenya Law.</li>
        <li>Each phone number came from the office’s own website.</li>
        <li>A date we couldn’t confirm isn’t printed: for registration dates, check iebc.or.ke.</li>
      </ul>
      <p class="checked-sw" lang="sw">Kila somo lina muhtasari kwa Kiswahili.</p>
    </div>
  </div>
</section>
<script>
(() => {{
  const tabs = [...document.querySelectorAll('.finder-tab')];
  const panels = [...document.querySelectorAll('.finder-answer')];
  if (!tabs.length) return;
  document.documentElement.classList.add('js');
  const show = (tab) => {{
    tabs.forEach((t) => t.setAttribute('aria-pressed', String(t === tab)));
    panels.forEach((p) => {{ p.hidden = p.id !== tab.getAttribute('aria-controls'); }});
  }};
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  tabs.forEach((t) => t.addEventListener('click', () => {{
    show(t);
    const panel = document.getElementById(t.getAttribute('aria-controls'));
    if (panel.getBoundingClientRect().top > innerHeight * 0.75) {{
      panel.scrollIntoView({{ block: 'start', behavior: still.matches ? 'auto' : 'smooth' }});
    }}
  }}));
  show(tabs[0]);
}})();
</script>"""
    return shell(page, "Katiba kwa Wote: the Constitution of Kenya in plain words",
                 "A free, plain-language course on the Constitution of Kenya, 2010, for ordinary Kenyans before the "
                 "2027 general election: your rights, voting, election offences, leaders and what to do if arrested.",
                 main)


def main() -> None:
    """Write every page and copy the assets into docs/."""
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "lessons").mkdir(parents=True)
    shutil.copytree(SITE / "assets", OUT / "assets")
    for name in ("tokens.css", "base.css", "site.css"):
        shutil.copy(SITE / "styles" / name, OUT / "assets" / name)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    all_lessons = lessons()
    (OUT / "index.html").write_text(home(all_lessons), encoding="utf-8")
    for les in all_lessons:
        (OUT / les["out"]).write_text(lesson_page(les, all_lessons), encoding="utf-8")
    for src, page in PAGES.items():
        if page.endswith(".html") and page != "index.html":
            (OUT / page).write_text(doc_page(src, page, all_lessons), encoding="utf-8")
    print(f"built {len(list(OUT.rglob('*.html')))} pages in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
