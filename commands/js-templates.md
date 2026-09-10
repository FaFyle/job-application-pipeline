---
description: Create your CV, cover-letter and prep-report templates - built from your own CV, once, then reused for every application.
---

# /js-templates

Produce the templates every generated application is built from, and save them in the
candidate's own data folder:

- `templates/cv-template.docx` — the CV, editable in Word by them and by you
- `templates/cover-letter-template.docx` — placeholders, kept deliberately plain
- `templates/prep-report-template.html` — the per-application briefing

**The CV is built per candidate, at runtime, from their own CV.** This plugin is
shared by many people: no CV design ships with it, and none ever should. Two people
running this command must end up with different-looking CVs. Never reach for a
"house style".

## Prerequisites

1. Read `~/.job-application-pipeline/config.json` for `data_root`. Missing -> tell the
   candidate to run `/js-setup`, stop.
2. Read `<data_root>/candidate/experience.json`. Missing -> `/js-interview` first,
   stop. If `meta.status` is `"in_progress"`, say so once and continue.
3. Check which templates already exist in `<data_root>/templates/`. Offer to build
   only what's missing, or to redo one they want changed.
4. Make sure the rendering toolchain is ready (below). Do this before generating
   anything - a CV you cannot look at is a CV you cannot verify.

## The toolchain

Scripts live in the plugin's `scripts/` directory (`${CLAUDE_PLUGIN_ROOT}/scripts/`;
if that isn't set, ask the candidate where the plugin is installed rather than
guessing). The Python side runs from a scratch virtualenv inside the data folder, so
the candidate's own Python is never touched:

```
python -m venv <data_root>/.tools/venv
<data_root>/.tools/venv/Scripts/python.exe -m pip install pymupdf pillow python-docx
```

Create it only if missing. On macOS/Linux the interpreter is `bin/python` rather than
`Scripts/python.exe`.

If Word is unavailable (non-Windows, or no Office), fall back to
`soffice --headless --convert-to pdf` — but **say plainly that you are previewing,
not verifying**: LibreOffice's layout engine differs from Word's enough to mislead,
and the candidate's employer will open the docx in Word. If neither renderer exists,
do not pretend the CV was checked; build it, say you could not see it, and ask the
candidate to open it and describe what's wrong.

## The build → verify loop

Never assert that a document looks right. Render it and look. One cycle takes a few
seconds, so iterate freely rather than batching guesses.

1. **Convert and count pages**:
   `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/docx_render.ps1 -Docx <in> -Pdf <out>`
   It prints `PAGES=n`. Check that first, on every build - it is the cheapest
   possible "does it still fit" test, and a CV that quietly became three pages is a
   real failure.
2. **Rasterize**: `python scripts/pdf_to_png.py <pdf> <dir> 110` — one PNG per page,
   ~910×1287 for A4. It clears previous PNGs itself; never skip that, or you will
   spend a cycle debugging an image of a document that no longer exists.
3. **Inspect twice.** Read the PNG and judge it as a document. Then measure it:
   `python scripts/measure_layout.py <dir> 21.0` reports margins, content width and
   anything touching the paper edge, in centimetres. Looking tells you "that seems
   narrow"; measuring tells you "the band is 19.5cm, not 17cm" - a specific fact you
   can fix. Both, every time. The measuring script is calibrated: on a known 2cm
   margin it reports 1.98-2.01cm, so treat its numbers as trustworthy.
4. Fix and repeat. Because `DisplayAlerts` is suppressed during conversion, a corrupt
   document would open silently - so a clean export plus a correct-looking render is
   also your file-validity check.

Run this loop on every variant before showing it, and again after every later edit.

## Working with real CVs in python-docx

Traps found in an actual candidate CV exported from a web CV builder:

- **Margins can be unparseable.** `section.left_margin` raises
  `ValueError: invalid literal for int()` when the file stores a non-integer twips
  value (e.g. `793.7007874015746`), which web-generated CVs routinely do. The
  document still opens fine — read `sectPr.xpath('./w:pgMar')` attributes directly,
  or wrap the accessor in `try/except`, rather than concluding the file is broken.
- **Two-column CVs are usually a table**, not Word columns. The one examined was a
  2-row x 3-column table: main content, a narrow gutter, and the sidebar. To change
  the layout you change the table; to keep the layout you must edit inside its cells.
- **Fonts are often set at style level, not on runs.** Iterating runs and reading
  `run.font.name` returns nothing useful. Change the *styles* to change the look —
  and this is precisely why editing their document can never produce a new design.
- Always check `len(doc.tables)` and the cell structure before assuming where content
  lives; text in a sidebar is not in `doc.paragraphs`.

## Part 0: preferences, before generating anything

Ask, one at a time, and store in `candidate/cv-preferences.json`:

- which sections to include, and in what order
- what the CV should lead with
- one page or two
- photo: yes or no — default from `preferences.json`'s `location`, since it is
  conventional in Switzerland, Germany and France and unusual in the US, UK and
  Ireland. Say which default you picked and why.
- personal details: date of birth, nationality, work permit — also regional
- the CV's language(s)
- how much detail per role
- which links to show
- what they dislike about their current CV

Then explain how the options differ, and **ask whether they want the two extra
options at all — say plainly that generating them takes noticeably longer and uses a
lot more tokens.** Default to one CV. Their choice, not yours.

## Part 1: the CV

Their CVs are in `<data_root>/source-documents/`, usually several of them.
`/js-interview` already took the *content* from all of them; what you need here is one
**design basis**, since Option A edits a document in place.

**Pick it without asking when you can.** Usually every CV is the same template
carrying different content. Compare the designs first:

- page setup — size and margins, read from the raw `w:pgMar` attributes (see the
  python-docx notes above: real CVs store non-integer twips the accessor can't parse)
- table structure, which is how two-column CVs are built — same shape or not
- the style names defined in the document, and the fonts on those styles, since fonts
  are set at style level rather than on runs
- heading treatment

If they match, choose one silently — the most recent, or the most complete when dates
are unclear — and say which in a line. **If they genuinely differ, ask which to use**,
and make clear the choice is only about looks: the content already came from all of
them, so nothing is lost either way. Cover letters are never a CV design basis.

If everything they have is a PDF, ask for a `.docx` re-save rather than inventing a
structure and calling it theirs.

Then take one of two branches. **Say which branch you are on** so the candidate knows
what to expect.

Both branches: ask for a profile picture if the preferences say photo, store it at
`candidate/photo.<ext>`, and place it with `add_picture`. Never invent one and never
drop it silently. Both branches also apply the interview's grounding flags — cut what
the candidate could not substantiate, add what surfaced only when asked, and tell
them what you changed and why, one line each.

### Branch 1 — they have a docx CV

**Option A — their own document, edited in place.** Open their `.docx` with
`python-docx` and update only the content, so their styles, fonts, spacing and
section structure survive exactly. Do not rebuild it and do not "tidy" their taste.
Faithful is the whole point: it gives them a baseline they recognise to judge the
others against.

Only if they asked for more — and these two must differ from each other on
*different axes*, or there is no reason to generate both:

- **Option B — better content and structure, same look.** Keep their visual design
  and edit in place as with A. What changes is the information: sharper bullets built
  from the interview's quantified evidence, skills grouped into meaningful labelled
  clusters instead of one undifferentiated block, sections added or reordered so the
  relevant material surfaces first, weak or unsupportable lines cut. Someone glancing
  at B should see their CV; someone reading it should find it markedly better.

- **Option C — visually redesigned, and modern.** This one is **built as a new
  document, not an edit of theirs.** Editing their file inherits their styles and you
  will produce another lookalike — that is exactly the failure this instruction
  exists to prevent. Create a fresh `Document()`, define your own styles, and commit
  to a deliberate visual direction: a different type pairing, your own section-header
  treatment, your own spacing rhythm and margins, your own grid (their sidebar is a
  table — you may change its proportions, swap which side it sits on, or drop the
  two-column structure entirely). Carry the same *content* as B; change how it looks.
  Modern here means typographic confidence and restraint — hierarchy through weight,
  size and whitespace rather than boxes and shaded panels; at most one accent colour;
  no skill rating bars, star ratings or percentage meters, even if their original has
  them.

**Write in their voice.** Any bullet you reword in A or B — and all of C's content —
follows `candidate/writing-style.json`, extracted from their own CVs and cover
letters. Respect its `avoid` list especially: a bullet that says "spearheaded" when
they have never written the word is the fastest way to make a CV read as
not-theirs. Style governs *how* something is written; it never licenses a claim they
cannot defend.

**Before showing B and C, render all three and look at them side by side.** If B and
C read as the same design, C has failed and must be rebuilt, not shipped with an
explanation. Say in one line what each option changed and what it trades away.

### Branch 2 — no usable CV

Covers someone who has never written one, and equally someone with only a PDF who
would rather not re-save it. Offer the re-save once, then move on; do not block.

- **All options here are proposals**, and say so — there is no original, so nothing
  is a baseline. Default to a single proposal; the same opt-in question covers
  whether they want two more.
- Ask the extra Part 0 questions in this branch only, since preferences are now the
  entire design input: overall tone (conservative, modern, editorial), how much white
  space, whether skills lead or support, and whether there is a CV they admire.
- **Generate the structure from those answers, their region and their field. Do not
  load a canned layout** — two candidates without CVs must not end up with the same
  document.
- Say plainly that this is not a downgrade: after `/js-interview`, `experience.json`
  is usually richer than the CV most people already have, so building from it tends
  to produce a better document than editing a thin one.

### Finishing

Save the chosen variant as `templates/cv-template.docx`, then write
`templates/.cv-template.snapshot.json` (see below) so later edits can be detected.

## Part 2: the cover-letter template

A plain `.docx` with placeholders — no design work, by decision. Their contact block,
date, recipient, salutation, three or four body paragraphs, sign-off. Mark the
per-application parts clearly (`{{company}}`, `{{role}}`, `{{opening}}`, `{{body_1}}`,
`{{body_2}}`, `{{closing}}`). PDF export is a manual print from Word; that is
deliberate, not a gap.

## Part 3: the prep-report template

Unlike the CV this presents pipeline output rather than the candidate's personal
presentation, so one layout serves everyone and it stays HTML. Build
`templates/prep-report-template.html` with a `JAP_PREP_DATA` block and the same
defensive normalization the other HTML pages use, covering: the job and its links,
the fit score with coverage/depth, **aligned with your profile** (matched
requirements plus the specific evidence behind each, so they can recall which story
to tell), **potential gaps** (unmatched requirements, must-haves first, framed as
what to be ready for), and anything else worth knowing before applying. Match the
scan dashboard's visual language.

## Editing later: read before you write

These documents are edited by both sides. Any command that modifies one must:

1. **Re-read the file first.** The candidate may have changed it in Word since you
   last wrote it. Never write from your memory of what it contained.
2. **Detect their edits** against `templates/.cv-template.snapshot.json` (hash, mtime,
   and extracted text at last write). If it differs, they edited it.
3. **Confront, don't overwrite.** If their change looks wrong — a required section
   gone, a claim the interview flagged as unsupportable put back, a broken layout —
   say what you see and ask. Do not silently revert it, and do not silently accept a
   claim they cannot defend.
4. **Re-verify after every change.** Run the build → verify loop again. A one-word
   edit can reflow a page, and presentation is most of what a CV is.

## Wrapping up

Confirm what was created, and name the command that generates an actual application —
or say plainly that it isn't built yet, if that's still true in this version.
