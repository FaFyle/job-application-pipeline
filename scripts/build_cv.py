"""Apply a set of edits to a .docx CV template, producing one application's CV.

Usage:
    python build_cv.py --template <in.docx> --out <out.docx> --plan <plan.json>
    python build_cv.py --template <in.docx> --plan <plan.json> --dry-run

The judgement - which bullets to sharpen for this posting, which roles to drop -
belongs to the command that writes the plan. This script only performs the edits
reliably, which on real .docx files is harder than it looks.

Plan format: {"edits": [ {...}, ... ]}, applied in order. Every op matches on a
literal substring, because that is what a language model can produce accurately from
having read the document.

    {"op": "replace_text",      "find": "...", "replace": "..."}
        Replace a substring wherever it appears, including inside table cells.

    {"op": "set_paragraph",     "match": "...", "text": "..."}
        Replace the whole text of the paragraph containing `match`, keeping the
        paragraph's style and its first run's formatting.

    {"op": "delete_paragraph",  "match": "..."}
        Delete the paragraph containing `match`.

    {"op": "delete_block",      "match": "...", "until_style": "Heading 2"}
        Delete the paragraph containing `match` and everything after it until the
        next paragraph with `until_style` - i.e. drop a whole CV entry.

    {"op": "add_bullet_after",  "match": "...", "text": "..."}
        Insert a new bullet after the paragraph containing `match`, cloning that
        paragraph's style so list formatting and indentation carry over.

Why matching is substring-based and run-aware: Word splits a paragraph's text across
runs at arbitrary points (spell-check, tracked formatting), so "Python" is often not
in any single run. Naively joining every run and rewriting the paragraph would fix
matching but destroy intra-paragraph formatting - and CV bullets routinely open with
a bold lead-in ("System implementation: ..."). So a match inside one run is replaced
in place, and only a match spanning several runs collapses those runs.
"""

import argparse
import copy
import json
import sys

from docx import Document


# --- locating text -----------------------------------------------------------

def iter_paragraphs(doc):
    """Every paragraph in the document, including inside tables.

    Two-column CVs are usually built as a table, so the sidebar's content is not in
    doc.paragraphs at all. Missing this is the most common way an edit silently does
    nothing.
    """
    for p in doc.paragraphs:
        yield p
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p
                for nested in cell.tables:
                    for nrow in nested.rows:
                        for ncell in nrow.cells:
                            for p in ncell.paragraphs:
                                yield p


def replace_in_paragraph(p, find, replace):
    """Replace `find` with `replace` in one paragraph. Returns True if it changed.

    Preserves run formatting when the match sits inside a single run, which is the
    common case and the one that matters for bold lead-ins.
    """
    for run in p.runs:
        if find in run.text:
            run.text = run.text.replace(find, replace)
            return True

    full = "".join(r.text for r in p.runs)
    if find not in full:
        return False

    # Spans runs: collapse into the first run. Formatting of the later runs is lost,
    # which is why the single-run path above is tried first.
    new = full.replace(find, replace)
    if not p.runs:
        return False
    p.runs[0].text = new
    for run in p.runs[1:]:
        run.text = ""
    return True


def delete_paragraph(p):
    el = p._element
    el.getparent().remove(el)


# --- operations --------------------------------------------------------------

def op_replace_text(doc, edit):
    find, replace = edit["find"], edit.get("replace", "")
    n = 0
    for p in iter_paragraphs(doc):
        if replace_in_paragraph(p, find, replace):
            n += 1
    return n, "replaced in %d paragraph(s)" % n


def op_set_paragraph(doc, edit):
    match, text = edit["match"], edit["text"]
    for p in iter_paragraphs(doc):
        if match in p.text:
            if p.runs:
                p.runs[0].text = text
                for run in p.runs[1:]:
                    run.text = ""
            else:
                p.add_run(text)
            return 1, "set paragraph"
    return 0, "no paragraph contained %r" % match


def op_delete_paragraph(doc, edit):
    match = edit["match"]
    for p in iter_paragraphs(doc):
        if match in p.text:
            delete_paragraph(p)
            return 1, "deleted paragraph"
    return 0, "no paragraph contained %r" % match


def op_delete_block(doc, edit):
    match = edit["match"]
    until = edit.get("until_style", "Heading 2")
    paras = list(iter_paragraphs(doc))
    start = None
    for i, p in enumerate(paras):
        if match in p.text:
            start = i
            break
    if start is None:
        return 0, "no paragraph contained %r" % match
    end = len(paras)
    for j in range(start + 1, len(paras)):
        if paras[j].style is not None and paras[j].style.name == until:
            end = j
            break
    for p in paras[start:end]:
        delete_paragraph(p)
    return end - start, "deleted %d paragraph(s)" % (end - start)


def op_add_bullet_after(doc, edit):
    match, text = edit["match"], edit["text"]
    for p in iter_paragraphs(doc):
        if match in p.text:
            new = copy.deepcopy(p._element)
            p._element.addnext(new)
            from docx.text.paragraph import Paragraph
            np = Paragraph(new, p._parent)
            if np.runs:
                np.runs[0].text = text
                for run in np.runs[1:]:
                    run.text = ""
            else:
                np.add_run(text)
            return 1, "added bullet"
    return 0, "no paragraph contained %r" % match


OPS = {
    "replace_text": op_replace_text,
    "set_paragraph": op_set_paragraph,
    "delete_paragraph": op_delete_paragraph,
    "delete_block": op_delete_block,
    "add_bullet_after": op_add_bullet_after,
}


# --- driver ------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template", required=True)
    ap.add_argument("--out")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.dry_run and not args.out:
        print("ERROR: --out is required unless --dry-run")
        return 2

    with open(args.plan, "r", encoding="utf-8") as fh:
        plan = json.load(fh)
    edits = plan.get("edits", [])
    if not edits:
        print("ERROR: plan contains no edits")
        return 2

    doc = Document(args.template)

    applied, failed = 0, 0
    for i, edit in enumerate(edits, 1):
        op = edit.get("op")
        fn = OPS.get(op)
        if fn is None:
            print("%2d. UNKNOWN OP %r" % (i, op))
            failed += 1
            continue
        try:
            count, detail = fn(doc, edit)
        except Exception as exc:  # a bad edit must not lose the other edits
            print("%2d. %-18s ERROR %s" % (i, op, exc))
            failed += 1
            continue
        if count:
            applied += 1
            print("%2d. %-18s %s" % (i, op, detail))
        else:
            # A silent no-op is the failure mode worth shouting about: the document
            # saves fine and looks untouched, and the tailoring never happened.
            failed += 1
            print("%2d. %-18s NO MATCH - %s" % (i, op, detail))

    print("\napplied %d, failed %d, of %d" % (applied, failed, len(edits)))

    if args.dry_run:
        print("dry run - nothing written")
    else:
        doc.save(args.out)
        print("wrote %s" % args.out)

    # Non-zero when anything failed, so the caller notices instead of shipping a CV
    # that was never actually tailored.
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
