#!/usr/bin/env python3
"""Extract per-tdoc decisions from a 3GPP RAN2 Chair's Notes .docx (optional).

The Chair's Notes (e.g. R2_134_ChairNotes_*.docx) repeats the agenda tree and,
under each item, lists every contribution followed by the decision the meeting
reached on it. In the file these are styled paragraphs: a "Doc-title" line starts
with the tdoc id, and any following "Agreement"/"Review-comment" line is the
outcome (Approved, Noted, Agreed, Revised to R2-..., etc.). This is richer than
the spreadsheet's one-word status, so use it to annotate tdocs with what actually
happened -- but it is optional; the skill works without it.

Standard library only. Usage:
    python read_chair_notes.py CHAIRNOTES.docx --json
    python read_chair_notes.py CHAIRNOTES.docx --agenda 8.1.2
    python read_chair_notes.py CHAIRNOTES.docx --tdoc R2-2603536

Each row:
    {"tdoc": "...", "agenda_item": "8.1.2", "agenda_title": "LCM for two-sided
     model", "decision": "Noted", "raw": "<concatenated doc-title text>"}
`decision` is empty when the notes list the tdoc but record no outcome.
"""
import sys, re, json, zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
TDOC_RE = re.compile(r'R\d+-\d{6,7}')
DECISION_STYLES = {'Agreement', 'Review-comment'}


def _paras(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    for p in root.iter(W + 'p'):
        txt = ''.join(t.text or '' for t in p.iter(W + 't')).strip()
        if not txt:
            continue
        pPr = p.find(W + 'pPr')
        style = ''
        if pPr is not None:
            ps = pPr.find(W + 'pStyle')
            if ps is not None:
                style = ps.get(W + 'val') or ''
        yield style, txt


def parse(path):
    rows = []
    cur_num = cur_title = ''
    cur = None  # the tdoc record currently accumulating decisions

    for style, txt in _paras(path):
        if style.startswith('Heading'):
            m = re.match(r'^(\d+(?:\.\d+)*)\s*(.*)$', txt)
            if m and m.group(2).strip():
                cur_num, cur_title = m.group(1), m.group(2).strip()
                cur = None
            continue

        if style == 'Doc-title':
            m = TDOC_RE.match(txt)
            if m:
                cur = {"tdoc": m.group(0), "agenda_item": cur_num,
                       "agenda_title": cur_title, "decision": "",
                       "raw": txt[m.end():].strip()}
                rows.append(cur)
            continue

        if style in DECISION_STYLES and cur is not None:
            cur["decision"] = (cur["decision"] + " " + txt).strip()

    return rows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    if not args:
        print(__doc__)
        sys.exit(1)
    rows = parse(args[0])

    if '--agenda' in sys.argv:
        want = sys.argv[sys.argv.index('--agenda') + 1]
        rows = [r for r in rows if r['agenda_item'] == want or r['agenda_item'].startswith(want + '.')]
    if '--tdoc' in sys.argv:
        want = sys.argv[sys.argv.index('--tdoc') + 1].lower()
        rows = [r for r in rows if r['tdoc'].lower() == want]

    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
