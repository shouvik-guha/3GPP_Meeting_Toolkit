# agenda-locator (portable skill)

Locate the 3GPP RAN2 agenda item for a topic or a tdoc, and list the
contributions filed under it with their source companies.

## Contents
```
agenda-locator/
├── SKILL.md                     # the skill: when it triggers + the procedure
├── references/
│   └── matching-guide.md        # release routing, sub-item rules, acronyms
└── scripts/                     # standard-library Python, no pip installs
    ├── extract_agenda.py        # agenda .docx  -> meeting no. + agenda tree
    ├── read_tdoc_list.py        # TDoc-list .xlsx -> tdocs + companies + status
    ├── scan_tdocs.py            # folder of tdoc .docx -> tdocs + companies
    └── read_chair_notes.py      # Chair's Notes .docx -> per-tdoc decisions (optional)
```

## Using it in different LLM tools
`SKILL.md` is plain Markdown, so it is portable:

- **Claude Code / Claude.ai skills:** copy the whole `agenda-locator/` folder
  into your skills directory (e.g. `.claude/skills/agenda-locator/` in a project,
  or `~/.claude/skills/agenda-locator/`).
- **Any other agent / LLM:** paste the contents of `SKILL.md` as a system or task
  instruction and make the `scripts/` and `references/` files available to the
  tool. The model runs the scripts and follows the procedure.

## Quick manual test
```bash
python scripts/extract_agenda.py <AGENDA.docx>
python scripts/read_tdoc_list.py <TDoc_List.xlsx> --agenda 8.1.2
python scripts/scan_tdocs.py <folder-of-tdocs> --tdoc R2-2601681
```
Requires only Python 3 (use `python3` if `python` is unavailable).
