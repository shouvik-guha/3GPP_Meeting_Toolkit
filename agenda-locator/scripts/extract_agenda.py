#!/usr/bin/env python3
"""Extract the meeting number and agenda tree from a 3GPP agenda .docx.

The agenda file is the one whose Title is "Agenda" (e.g. R2-2602901.docx). It
contains the meeting header plus the heading hierarchy (section number + title).
This script does NOT need pandoc, defusedxml, or any third-party library -- it
reads the docx (a zip of XML) with the Python standard library only, so it runs
in any environment.

Usage:
    python extract_agenda.py AGENDA.docx            # human-readable
    python extract_agenda.py AGENDA.docx --json     # JSON for downstream steps

JSON shape:
    {
      "meeting": "RAN2#134",
      "meeting_raw": "3GPP TSG-RAN WG2 Meeting #134",
      "location_dates": "Dalian, May 18th - 22nd",
      "agenda": [ {"number": "8.1.2", "title": "LCM for two-sided model"}, ... ]
    }
"""
import sys, re, json, zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def _text(p):
    return ''.join(t.text or '' for t in p.iter(W + 't')).strip()


def _style(p):
    pPr = p.find(W + 'pPr')
    if pPr is None:
        return ''
    ps = pPr.find(W + 'pStyle')
    return ps.get(W + 'val') if ps is not None else ''


def parse(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
    root = ET.fromstring(xml)

    paras = [(_style(p), _text(p)) for p in root.iter(W + 'p')]
    paras = [(s, t) for s, t in paras if t]

    # --- meeting metadata: first non-empty lines carry the header ---
    meeting_raw = location_dates = meeting = None
    for _, t in paras[:8]:
        # meeting number is digits + optional lowercase suffix (e.g. 134, 133bis);
        # bound it so an immediately-following tdoc id like "R2-2602901" is not swallowed.
        m = re.search(r'(TSG[- ]?RAN\s*WG\s*\d+|RAN\s*WG\s*\d+|TSG[- ]?RAN\d*).*?Meeting\s*#?\s*(\d+(?:bis|ter)?)', t, re.I)
        if m and meeting_raw is None:
            meeting_raw = re.sub(r'R\d-\d{7}.*$', '', t).strip()  # strip trailing tdoc id
            wg = re.search(r'WG\s*(\d+)', t, re.I)
            meeting = f"RAN{wg.group(1)}#{m.group(2)}" if wg else f"#{m.group(2)}"
        # location/date line usually contains a month name or an en dash range
        if location_dates is None and re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*', t) \
                and not re.match(r'^\d', t):
            location_dates = t

    # --- agenda tree: heading paragraphs, split leading number from title ---
    agenda = []
    for style, t in paras:
        if 'Heading' not in style:
            continue
        m = re.match(r'^(\d+(?:\.\d+)*)\s*(.*)$', t)
        if not m:
            continue
        num, title = m.group(1), m.group(2).strip()
        if title:  # skip stray numbers with no title
            agenda.append({"number": num, "title": title})

    return {
        "meeting": meeting,
        "meeting_raw": meeting_raw,
        "location_dates": location_dates,
        "agenda": agenda,
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    as_json = '--json' in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)
    data = parse(args[0])
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"Meeting : {data['meeting']}  ({data['meeting_raw']})")
        print(f"When    : {data['location_dates']}")
        print(f"Sections: {len(data['agenda'])}\n")
        for a in data['agenda']:
            print(f"{a['number']}\t{a['title']}")


if __name__ == '__main__':
    main()
