# agenda-locator — eval results (iteration 1)

8 topic/tdoc queries on the real RAN2#134 files, each run **with the skill** and as a
**baseline** (no skill, same files + tools). Ground truth verified against the TDoc list.

## Accuracy: tie at 8/8

| # | Query | Correct | with-skill | baseline |
|---|-------|---------|:--:|:--:|
| 0 | LCM for two-sided model | 8.1.2 | ✅ | ✅ |
| 1 | AI/ML air-interface corrections, Rel-19 | 7.1.2 | ✅ | ✅ |
| 2 | RRM measurement prediction (AI/ML mobility) | 8.3.2 | ✅ | ✅ |
| 3 | Network Energy Saving corrections, Rel-19 | 7.5.2 | ✅ | ✅ |
| 4 | IoT NTN Phase 4 SPS solution | 8.7.2 | ✅ | ✅ |
| 5 | tdoc R2-2603536 (id lookup) | 8.1.2 | ✅ | ✅ |
| 6 | SBFD corrections | 7.11.2 | ✅ | ✅ |
| 7 | AI/ML data collection (ambiguous) | 8.1.3 / 8.3.4 | ✅ both + alt | ✅ both + alt |

Every run avoided the release/domain traps (Rel-18 vs 19 vs 20; AI/ML air vs mobility)
and both configs flagged eval-7 as genuinely ambiguous, choosing 8.3.4 with 8.1.3 as the
alternative.

## Speed / tokens

| Config | Accuracy | Avg tokens | Avg wall-clock |
|--------|:--:|--:|--:|
| with-skill    | 8/8 | 42,027 | **63.2 s** |
| baseline      | 8/8 | 34,453 | 81.2 s |
| delta (skill−baseline) | 0 | +7,574 | **−18.0 s** |

## Interpretation

- **A frontier model handed the agenda `.docx` + TDoc list solves the classification on
  its own** — so the skill is *not* the thing that makes the answer correct here.
- The skill's payoff is elsewhere: it is **~22% faster wall-clock** (deterministic scripts
  instead of each agent hand-rolling a docx/xlsx parser), it **pre-solves the xlsx
  "Agenda item sort order" column trap**, and it emits a **consistent structured output**
  (meeting → agenda → tdocs + companies + decision) every time. It costs ~7.5k extra
  tokens per run to read SKILL.md + references.
- Expected to matter more where this eval can't show it: **weaker/smaller models**, **bulk
  automation** (hundreds of lookups), and **portability** to non-Claude LLMs.

## Takeaway for the skill
No classification failures to fix. If optimizing further, the lever is **leanness**: the
+7.5k token overhead suggests trimming SKILL.md / making the matching-guide load only when
a topic is ambiguous, so simple lookups stay cheap.
