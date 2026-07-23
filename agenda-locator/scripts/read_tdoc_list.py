#!/usr/bin/env python3
"""Read a 3GPP TDoc-list spreadsheet (.xlsx) into normalized rows.

The 3GPP server publishes a per-meeting "TDoc_List_Meeting_RAN2#NNN.xlsx" with one
row per contribution and columns such as: TDoc, Title, Source, Type, For,
Agenda item, Agenda item description. This is the authoritative agenda -> tdoc ->
company mapping. This script parses it with the standard library only (an .xlsx is
a zip of XML), so no pandas/openpyxl is required.

Usage:
    python read_tdoc_list.py TDOC_LIST.xlsx --json
    python read_tdoc_list.py TDOC_LIST.xlsx --agenda 8.1.2     # filter to one item
    python read_tdoc_list.py TDOC_LIST.xlsx --tdoc R2-2601681  # look up one tdoc

Each row is normalized to:
    {"tdoc": "...", "title": "...", "source": "...", "agenda_item": "...",
     "agenda_title": "...", "type": "...", "for": "..."}
Column names are matched case-insensitively and fuzzily, so minor header
variations across meetings still work.
"""
import sys, re, json, zipfile
import xml.etree.ElementTree as ET

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

# canonical field -> candidate header names, best/most-specific first.
# Matching is exact-name-first (see _build_colmap): this is what stops
# "Agenda item" from being shadowed by "Agenda item sort order" or
# "Agenda item description", which merely *contain* the words "agenda item".
FIELD_HINTS = {
    "tdoc":         ["tdoc", "td number", "document number", "document"],
    "title":        ["title", "subject"],
    "source":       ["source"],
    "type":         ["type"],
    "for":          ["for", "document for"],
    "agenda_item":  ["agenda item", "agenda number", "ai number"],
    "agenda_title": ["agenda item description", "agenda title", "agenda description"],
    "status":       ["tdoc status", "status"],
    "rel":          ["rel", "release"],
}

# headers containing any of these are never treated as a data column, so a
# "... sort order" helper column can't be mistaken for the field it sorts.
NOISE = ("sort order",)


def _shared_strings(z):
    try:
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    except KeyError:
        return []
    out = []
    for si in root.findall(NS + 'si'):
        # a string item may hold direct <t> or several <r><t> runs
        out.append(''.join(t.text or '' for t in si.iter(NS + 't')))
    return out


def _col_index(ref):
    # "B7" -> 1 (zero-based column)
    letters = re.match(r'[A-Z]+', ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _first_sheet_path(z):
    names = [n for n in z.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml$', n)]
    names.sort(key=lambda n: int(re.search(r'(\d+)', n).group(1)))
    return names[0]


def _rows(z, shared):
    root = ET.fromstring(z.read(_first_sheet_path(z)))
    for row in root.iter(NS + 'row'):
        cells = {}
        for c in row.findall(NS + 'c'):
            ref = c.get('r')
            if not ref:
                continue
            idx = _col_index(ref)
            v = c.find(NS + 'v')
            if v is None:
                # inline string
                is_ = c.find(NS + 'is')
                val = ''.join(t.text or '' for t in is_.iter(NS + 't')) if is_ is not None else ''
            elif c.get('t') == 's':
                val = shared[int(v.text)] if v.text and v.text.isdigit() else ''
            else:
                val = v.text or ''
            cells[idx] = val.strip()
        yield cells


def _build_colmap(header):
    """Map each canonical field to a column index.

    Two passes so exact header names win over mere substring hits: the real 3GPP
    list has "Agenda item", "Agenda item sort order" and "Agenda item description"
    side by side, and only exact-first matching routes each correctly.
    """
    norm = {idx: (name or '').strip().lower() for idx, name in header.items()}
    norm = {idx: low for idx, low in norm.items() if not any(n in low for n in NOISE)}
    colmap = {}
    # pass 1: exact header == candidate name
    for field, names in FIELD_HINTS.items():
        for idx in sorted(norm):
            if norm[idx] in names:
                colmap[field] = idx
                break
    # pass 2: substring fallback for anything still unmapped
    for field, names in FIELD_HINTS.items():
        if field in colmap:
            continue
        for idx in sorted(norm):
            if idx in colmap.values():
                continue
            if any(n in norm[idx] for n in names):
                colmap[field] = idx
                break
    return colmap


def parse(path):
    with zipfile.ZipFile(path) as z:
        shared = _shared_strings(z)
        rows = list(_rows(z, shared))
    if not rows:
        return []

    # find the header row: the first row that mentions "tdoc" and "title"
    header_i = 0
    for i, r in enumerate(rows[:15]):
        joined = ' '.join(v.lower() for v in r.values())
        if 'tdoc' in joined and 'title' in joined:
            header_i = i
            break
    header = rows[header_i]
    colmap = _build_colmap(header)

    out = []
    for r in rows[header_i + 1:]:
        rec = {f: r.get(idx, '') for f, idx in colmap.items()}
        if not any(rec.values()):
            continue
        if not rec.get("tdoc"):
            continue
        for f in FIELD_HINTS:
            rec.setdefault(f, '')
        out.append(rec)
    return out


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
