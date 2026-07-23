# 3GPP Meeting Toolkit

Tools for working with 3GPP TSG-RAN meeting artifacts — agendas, TDoc lists, and
Chair's Notes. Everything here is standard-library Python (no `pip install` needed)
so the scripts run anywhere, and the skills are plain Markdown so they port across
LLM tools.

## Contents

### [`agenda-locator/`](agenda-locator/) — skill
Given a topic or a tdoc id, locate the correct agenda item for a RAN meeting and
list the contributions filed under it with their **source companies** and
**decisions/status**. Works across meetings and across three source formats:

- **agenda `.docx`** → meeting number + full agenda tree
- **TDoc-list `.xlsx`** → tdocs, companies, status, release
- **folder of tdoc `.docx`** → tdocs + companies (cover-page parsing)
- **Chair's Notes `.docx`** *(optional)* → per-tdoc decisions (Agreed / Noted / …)

See [`agenda-locator/SKILL.md`](agenda-locator/SKILL.md) for the procedure and
[`agenda-locator/README.md`](agenda-locator/README.md) for install/usage.

#### Validation
The skill was evaluated on real RAN2#134 data (see
[`agenda-locator/evals/results/`](agenda-locator/evals/results/)):
- **Frontier model:** 8/8 classification accuracy (ties an unaided baseline — the
  skill's value there is speed + consistent structured output).
- **Weaker model (Haiku), hard queries:** **8/8 with skill vs 6/8 baseline** — the
  matching guide's release-routing and sub-item conventions caught cases the
  baseline missed (e.g. Rel-17 NR NTN 5.3 vs the EUTRA NTN 4.3 trap).

## Using the skill in an LLM tool
Copy `agenda-locator/` into your skills directory (e.g. `.claude/skills/` for a
project, or `~/.claude/skills/`), or paste `SKILL.md` as a system/task instruction
and expose the `scripts/` and `references/` files.

## Requirements
Python 3 (use `python3` if `python` is unavailable). No third-party libraries.
