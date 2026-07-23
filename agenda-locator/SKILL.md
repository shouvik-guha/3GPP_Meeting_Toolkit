---
name: agenda-locator
description: >-
  Locate the 3GPP agenda item for a topic or a tdoc, and list the contributions
  (tdocs) filed under it together with their source companies. Use this whenever
  the user references a 3GPP RAN meeting agenda, an agenda item number (e.g.
  "8.1.2"), a work item or feature by name or acronym (LCM, NES, LTM, SBFD, NTN,
  AI/ML, XR, MIMO, SON/MDT...), or a tdoc id (e.g. R2-2601681), and wants to know
  which agenda item it belongs to, what the meeting is, or which companies
  submitted papers under that item. Trigger it for phrasings like "which agenda
  is this about", "find the agenda item for two-sided model LCM", "list the
  tdocs and companies under 8.1.2", or "what agenda is R2-2601681" — even when
  the user does not say the word "agenda". Works across multiple meetings and
  multiple agenda documents.
---

# Agenda locator

Given a user request, this skill finds the right 3GPP agenda item and reports the
tdocs (contributions) filed under it with their source companies. It works from
two kinds of 3GPP artifacts and does not depend on any third-party library — the
bundled scripts read `.docx` and `.xlsx` with the Python standard library, so
they run anywhere.

## What the user gives you
Two independent pieces of input:

1. **A query** — either
   - a **topic / feature** ("LCM for two-sided model", "Rel-19 network energy
     saving corrections"), or
   - a **tdoc id** ("R2-2601681").
2. **Source files** — some combination of:
   - an **agenda `.docx`** (its Title is "Agenda", e.g. `R2-2602901.docx`) — gives
     the meeting number and the full agenda tree;
   - a **tdoc source** for the company data: a **TDoc-list `.xlsx`**
     (e.g. `tdocList_*.xlsx` / `TDoc_List_Meeting_RAN2#NNN.xlsx`) and/or a
     **folder of individual tdoc `.docx` files**; and
   - **optionally**, a **Chair's Notes `.docx`** (e.g. `R2_134_ChairNotes_*.docx`)
     — extra metadata giving the **decision/outcome** recorded for each tdoc
     (Approved, Noted, Agreed, "Revised to R2-…", "The CR is agreed", etc.).

If a needed file is not provided, ask the user for it (say which one and why). The
Chair's Notes is a bonus, not a requirement — use it to enrich the output when
present, but never block on it.

The `.xlsx` is the authoritative agenda→tdoc→company map; prefer it when present
and fall back to scanning the tdoc folder otherwise. It also carries each tdoc's
one-word `status` (available / noted / revised / withdrawn / agreed …) and release
(`rel`), which you can report even without the Chair's Notes.

## Output format
Always report in this structure:

```
Meeting: <meeting number> — <location, dates if known>
Agenda:  <number>  <title>
Confidence: <High | Medium | Low>   (omit this line for a direct tdoc lookup)
Reason:  <one sentence: the feature + release that drove the match>

Tdocs under this agenda (<count>):
  <tdoc>   <source company>   —   <title>   [<status/decision>]
  <tdoc>   <source company>   —   <title>   [<status/decision>]
  ...

Alternatives: <number title; number title — or "None">
```

The trailing `[<status/decision>]` is optional: show the tdoc's `status` from the
`.xlsx`, and if the Chair's Notes gave an explicit decision, prefer that wording
(e.g. `[Noted]`, `[The CR is agreed]`). Omit the bracket when neither is known.

When the user asked for JSON, return the same fields as a JSON object with an
`agenda` object, a `meeting` string, and a `tdocs` array of
`{tdoc, source, title, status, decision}`.

## Procedure

### Step 1 — read the agenda tree and meeting number
Run the extractor on the agenda `.docx`:

```
python scripts/extract_agenda.py <AGENDA.docx> --json
```

It returns `{meeting, meeting_raw, location_dates, agenda:[{number,title}]}`. Keep
the full agenda list — you will match against it and resolve titles from it.

### Step 2 — resolve the agenda item

**If the query is a tdoc id** (matches `R\d+-\d{6,7}`): look it up directly in the
tdoc source (Step 3 tools accept `--tdoc <id>`). The tdoc's own `agenda_item`
field is the answer — trust it over your own guess. Resolve its title from the
agenda tree. This is a direct lookup, so no confidence rating is needed.

**If the query is a topic**: classify it against the agenda tree. Read
`references/matching-guide.md` and apply it — it covers release routing (the most
common mistake), the `.0/.1/.2` sub-item conventions, and acronym expansion.
Choose the single **deepest** agenda item that fits; if several fit equally, note
up to two alternatives. Never invent a number that is not in the agenda tree.

### Step 3 — list the tdocs and companies under that item

From a **TDoc-list `.xlsx`** (preferred):

```
python scripts/read_tdoc_list.py <TDoc_List.xlsx> --agenda <number>
```

From a **folder of tdoc `.docx`** files:

```
python scripts/scan_tdocs.py <folder> --agenda <number>
```

Both accept `--agenda <number>` (also returns tdocs in deeper sub-items, e.g.
`--agenda 8.1` includes `8.1.2`) or `--tdoc <id>` for a single lookup. The `.xlsx`
reader emits `{tdoc, title, source, agenda_item, agenda_title, status, rel, type,
for}`; the folder scanner emits the same fields minus `status`/`rel`. Use `source`
as the company. If both sources are available, use the `.xlsx`; only scan the
folder when there is no spreadsheet.

### Step 3b — enrich with decisions (only if Chair's Notes provided)
When a Chair's Notes `.docx` is available, pull the recorded outcome per tdoc:

```
python scripts/read_chair_notes.py <ChairNotes.docx> --agenda <number>
python scripts/read_chair_notes.py <ChairNotes.docx> --tdoc <id>
```

It emits `{tdoc, agenda_item, agenda_title, decision, raw}`. Join it to the Step 3
rows on `tdoc` and use `decision` as the outcome (it is empty for tdocs that were
listed but not individually decided — fall back to the `.xlsx` `status` there). The
notes also record which agenda item each tdoc was actually treated under, so for a
tdoc lookup they corroborate (or, rarely, correct) the spreadsheet's agenda item.

### Step 4 — assemble the report
Fill the output template with the meeting number (Step 1), the resolved agenda
number + title, the tdoc rows (Step 3), and any decisions (Step 3b). Sort tdocs by
tdoc id. If the item has no tdocs, say so plainly rather than leaving the list
blank.

## Multiple meetings / documents
Each meeting has its own agenda `.docx` and its own tdoc source. When the user
has several, key everything off the file that matches the query's meeting: run
Step 1 on that meeting's agenda, and Step 3 on the same meeting's tdoc source.
Do not mix tdocs from one meeting with the agenda tree of another — agenda
numbering shifts between meetings.

## Notes on robustness
- The scripts are standard-library only; if `python` is unavailable, `python3`
  works identically.
- Column headers in the `.xlsx` and label wording in tdoc covers vary slightly
  between meetings; the scripts match them fuzzily. If a field comes back empty,
  fall back to reading the file directly to confirm before reporting a gap.
- Source company strings may list several companies ("Nokia, Nokia Shanghai
  Bell") — keep them verbatim.
