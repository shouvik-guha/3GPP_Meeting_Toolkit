#!/usr/bin/env python3
"""Scan a folder of individual 3GPP tdoc .docx files and pull cover-page fields.

Every 3GPP contribution starts with a standard cover table whose labelled rows
include "Agenda item:", "Source:" (or "Source to ..."), "Title:", and
"Document for:". This script reads each .docx's text (standard library only) and
extracts those fields, plus the tdoc number (from the filename R2-NNNNNNN or the
document header). Use it when you have the tdoc files themselves rather than the
TDoc-list spreadsheet.

Usage:
    python scan_tdocs.py FOLDER --json
    python scan_tdocs.py FOLDER --agenda 8.1.2
    python scan_tdocs.py FOLDER --tdoc R2-2601681

Output rows match read_tdoc_list.py:
    {"tdoc", "title", "source", "agenda_item", "agenda_title", "type", "for"}
(agenda_title is left blank here -- resolve it from the agenda tree downstream.)
"""
import sys, os, re, json, zipfile, glob
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

LABELS = {
    "agenda_item": [r'agenda\s*item'],
    "source":      [r'source(?:\s*to\s*[\w\s]+)?'],
    "title":       [r'title'],
    "for":         [r'document\s*for', r'^for$'],
}


def _paragraphs(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    for p in root.iter(W + 'p'):
        txt = ''.join(t.text or '' for t in p.iter(W + 't')).strip()
        if txt:
            yield txt


def _label_of(text):
    # returns (field, inline_value) for a line like "Agenda item:\t8.1.2",
    # or (field, "") when the label stands alone in its own table cell.
    m = re.match(r'\s*([A-Za-z][A-Za-z /]*?)\s*[:：]\s*(.*)$', text)
    if not m:
        return None, None
    label, value = m.group(1).strip().lower(), m.group(2).strip()
    for field, pats in LABELS.items():
        if any(re.fullmatch(p, label, re.I) for p in pats):
            return field, value
    return None, None


def scan_file(path):
    rec = {"tdoc": "", "title": "", "source": "", "agenda_item": "",
           "agenda_title": "", "type": "", "for": ""}

    # tdoc number: filename first, then any R#-####### in the text
    base = os.path.splitext(os.path.basename(path))[0]
    fm = re.search(r'R\d+-\d{6,7}', base)
    if fm:
        rec["tdoc"] = fm.group(0)

    paras = list(_paragraphs(path))
    for i, t in enumerate(paras):
        field, value = _label_of(t)
        if field and not rec[field]:
            if not value:
                # label alone in its cell -> value is the next non-empty paragraph
                # (2-column cover table), as long as that isn't itself a label.
                for nxt in paras[i + 1:i + 3]:
                    nf, _ = _label_of(nxt)
                    if nf is None:
                        value = nxt
                        break
            if value:
                rec[field] = value
        if not rec["tdoc"]:
            tm = re.search(r'R\d+-\d{6,7}', t)
            if tm:
                rec["tdoc"] = tm.group(0)

    # normalize agenda_item to just the number token if extra text trails it
    if rec["agenda_item"]:
        am = re.match(r'(\d+(?:\.\d+)*)', rec["agenda_item"])
        if am:
            rec["agenda_item"] = am.group(1)
    return rec


def parse(folder):
    files = sorted(glob.glob(os.path.join(folder, '**', '*.docx'), recursive=True))
    files = [f for f in files if not os.path.basename(f).startswith('~$')]
    rows = []
    for f in files:
        try:
            rows.append(scan_file(f))
        except Exception as e:
            sys.stderr.write(f"skip {f}: {e}\n")
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
