# Katiba kwa Wote · The Constitution for everyone

A free, plain-language course on the **Constitution of Kenya, 2010**, for ordinary Kenyans, ahead of the
**general election on Tuesday, 10 August 2027**.

No law degree needed. No school background needed. Short sentences, everyday Kenyan examples, and the Article number
for every rule, so you can check the real words yourself.

> **Kwa ufupi (Kiswahili):** Kozi hii ya bure inaeleza Katiba ya Kenya kwa lugha rahisi: haki zako, jinsi ya
> kujiandikisha na kupiga kura, makosa ya uchaguzi, uadilifu wa viongozi, kazi ya kila kiongozi unayemchagua, jinsi
> ya kushiriki maamuzi, na la kufanya ukikamatwa. Kila somo linaisha na "Unachoweza kufanya" na "Mahali pa kwenda".

---

## The course map

Read the lessons in order, or jump to the one you need today. Each takes about 10 to 12 minutes, and each ends with
**What you can do**, **Where to go**, and a short quiz.

| # | Lesson | You'll learn | Key Articles |
|---|---|---|---|
| 1 | [Your rights](lessons/01-your-rights.md) | What a right is, and how to remember yours in three groups | 3, 19 to 59 |
| 2 | [Registering and voting](lessons/02-registering-and-voting.md) | Who can register, how to check your details, the six ballots, how a president wins | 38, 83, 86, 101, 138 |
| 3 | [What's illegal in an election, and how to report it](lessons/03-election-crimes-and-reporting.md) | Vote buying, violence, misuse of government resources, hate speech | 33, 81, 84, 91 |
| 4 | [When an election result is disputed](lessons/04-election-disputes.md) | Which court, which deadline, and the 2017 case | 86, 87, 105, 140 |
| 5 | [Leadership and integrity: how to judge a candidate](lessons/05-leadership-and-integrity.md) | Chapter Six, who can't stand, and questions to ask | 73 to 80, 99, 193 |
| 6 | [Who does what: your six leaders and your county](lessons/06-who-does-what.md) | What the President, MP, Woman Member, Senator, Governor and MCA each actually do | 95 to 98, 174 to 185, Fourth Schedule |
| 7 | [Having your say, and recalling leaders](lessons/07-public-participation-and-recall.md) | Public participation, petitions, information, and recall | 1, 35, 104, 118, 119, 196 |
| 8 | [If you're arrested, or your rights are violated](lessons/08-arrested-or-rights-violated.md) | The 24-hour rule, a fair trial, habeas corpus, and where to complain | 22, 23, 25, 49 to 51 |

### Also in this course

- **[Where to go](WHERE-TO-GO.md):** every office, hotline and website, checked on the offices' own sites.
- **[Glossary](GLOSSARY.md):** the legal words, explained once, in plain language.
- **[2027 election checklist](checklists/election-2027-checklist.md):** print it, tick it.
- **[Sources](SOURCES.md):** every Article, Act and case used, with links.

---

## How this course was checked

- **Every rule** was checked against the official text of the Constitution and the Acts of Parliament on
  [Kenya Law](https://kenyalaw.org). Article and section numbers are given so you can check them too.
- **Every phone number** was copied from that office's own website, and all of them live in one place,
  [WHERE-TO-GO.md](WHERE-TO-GO.md).
- **Dates we couldn't confirm aren't printed.** For voter registration dates, the course says "check
  [iebc.or.ke](https://www.iebc.or.ke)".
- **Real events are labelled.** *Confirmed* means a court ruling, an official record or several reliable reports
  agree. *Yet to be confirmed* comes with the date we last checked.
- **Otieno and Akinyi are made up.** They stand in for you and your neighbours. Every example with numbers says so
  when the numbers are made up.

Last checked: **Friday, 27 November 2026.**

> **Please note:** this course explains the law in everyday language. It is **not legal advice**. For your own case,
> speak to an advocate, or contact the **National Legal Aid Service** (toll free 0800 720 640). The course takes **no
> side** in any election, party or candidate.

---

## Help improve it

Found a number that changed, a law that was amended, or a mistake? Open an issue or a pull request, **with a link to
the official source**: the office's own website, or the law on Kenya Law.

Before you send a change, run the checks (Python 3, no installs needed):

```bash
make check
```

It confirms that every lesson keeps its required sections, every phone number appears in
[WHERE-TO-GO.md](WHERE-TO-GO.md), and every internal link works.

Translations, especially full Kiswahili versions of the lessons, are very welcome.

### The website

The same course is published as a website with GitHub Pages, built from these Markdown files into `docs/`. After
changing a lesson, rebuild it (Python 3 with the `markdown` package):

```bash
make site
```

The site's look comes from the author's video series on the Constitution: its colours, its typeface (Noto Serif)
and its illustrations.

---

## Licence

© 2026 sagebeme. This course is licensed under the
[Creative Commons Attribution 4.0 International licence (CC BY 4.0)](LICENSE). You may share and adapt it, for any
purpose, as long as you give credit and say what you changed.

The Constitution and Acts of Parliament quoted here are Kenyan law. Kenya Law's own website content has its own
terms: see [kenyalaw.org](https://kenyalaw.org).
