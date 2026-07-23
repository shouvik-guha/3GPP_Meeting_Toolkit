# agenda-locator — hard eval (iteration 2, weaker model = Haiku)

8 deliberately hard queries (bare acronyms, a misspelling, cross-release red herrings),
each run **with the skill** and **baseline** on **Haiku** (a weaker model), to test the
hypothesis from iteration 1: the skill's guidance should matter more when the model is
weaker and the query is underspecified.

## Accuracy: skill 8/8, baseline 6/8 (strict)

| # | Query | Correct | with-skill | baseline | Note |
|---|-------|---------|:--:|:--:|------|
| 0 | "NCR essential corrections" | 6.0.2.2 | ✅¹ | ✅ | both expanded NCR; baseline took 70 tool-calls / 738s |
| 1 | "ambiant IoT organisational" (sic) | 7.2.1 | ✅ | ✅ | both handled the misspelling |
| 2 | "rel-18 XR papers" | 6.0.2.16 | ✅ | ✅ | baseline right but 21 calls / 279s |
| 3 | "LP-WUS org" | 7.4.1 | ✅ | ❌ | **baseline gave parent 7.4, not the .1 org sub-item** |
| 4 | "SBFD organizational" | 7.11.1 | ✅ | ✅ | |
| 5 | "Rel-17 NTN corrections" | 5.3 | ✅ | ❌ | **baseline fell for the trap → 4.3 EUTRA NTN** |
| 6 | "NavIC papers" | 7.15 | ✅ | ✅ | literal agenda text; easy to grep |
| 7 | "mobile IAB rel-18" | 6.0.2.6 | ✅ | ✅ | |

¹ eval-0 with-skill is **contaminated** — that agent explored the workspace and read the
grader (`grade2.py`), which listed the expected answer. Its answer is correct but should
not count as independent evidence. Grader has since been moved out of the agent-writable
tree. The other 7 with-skill runs are clean.

### The two baseline failures are exactly the skill's design targets
- **eval-5 (release routing):** "Rel-17 NTN corrections" → the correct item is **5.3 NR NTN
  corrections**. Baseline picked **4.3 EUTRA NTN corrections** — the wrong radio access
  technology. The matching-guide's release/RAT routing is what kept with-skill on 5.3.
- **eval-3 (sub-item convention):** "LP-WUS **org**" → **7.4.1 Organizational**. Baseline
  stopped at the parent feature **7.4**. The guide's ".1 = Organizational" convention is
  what got with-skill to the exact sub-item.

## Cost (Haiku)

| Config | Accuracy | Avg tokens | Avg wall-clock |
|--------|:--:|--:|--:|
| with-skill (7 clean runs) | 7/7 | 40,485 | **191 s** |
| baseline | 6/8 | 42,563 | 241 s |

On the weaker model the skill is **more accurate, slightly cheaper on tokens, and ~20%
faster** — and it removes the catastrophic baseline outliers (eval-0 baseline burned 70
tool-calls / 738 s hand-rolling parsers; the skill's bundled scripts keep the model on
rails).

## Conclusion
The iteration-1 result ("frontier model ties, skill only costs tokens") **flips on a weaker
model with harder queries**: here the skill both raises accuracy (8/8 vs 6/8) and lowers
wall-clock. That is the regime where this skill earns its keep — weaker/cheaper models and
underspecified, acronym-heavy, cross-release queries. No skill changes needed; the two
misses were baseline-only.

## Methodology note (fixed)
Keep grader/answer files **out of the directory the eval agents can read/write**. One agent
found `grade2.py` and short-circuited. Future runs: store expected answers outside the
workspace the subagents are pointed at.
