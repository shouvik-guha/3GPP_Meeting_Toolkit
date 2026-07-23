# 3GPP RAN2 agenda-matching guide

This guide helps map a free-text topic to the correct agenda item. It exists
because 3GPP contributions describe work items by acronym and release, and a naive
keyword match routes them to the wrong section (wrong release, wrong sub-item).

## Table of contents
- [How to choose the right item](#how-to-choose-the-right-item)
- [Release routing](#release-routing) — the single most common mistake
- [Sub-item conventions](#sub-item-conventions)
- [Acronym expansion](#acronym-expansion)

## How to choose the right item
Match on the **work item / feature and its release**, not on surface words:
1. Identify the feature (expand the acronym — see below).
2. Identify the release (Rel-17/18/19/20 or 6G study) from explicit cues
   ("Rel-19", "R20", "6G", "Study on…") or from which meeting phase the feature
   belongs to.
3. Pick the **deepest** agenda item that still fits. `8.1.2 LCM for two-sided
   model` beats `8.1 AI/ML for PHY Ph2` beats `8 NR Rel-20`.
4. If several items fit equally, return the top candidate plus up to two
   alternatives rather than forcing one.

## Release routing
The same feature name recurs across releases under different top-level sections.
Route by release first, then by feature:

| Release cue | Top section |
|---|---|
| Rel-17 or earlier, "legacy", maintenance of old features | 5 — NR Rel-17 and earlier |
| Rel-18 | 6 — NR Rel-18 |
| Rel-19 | 7 — NR Rel-19 |
| Rel-20 | 8 — NR Rel-20 |
| 6G, "Study on 6G", 6G Radio | 9 — 6GR Rel-20 Study |
| EUTRA / LTE corrections | 4 — EUTRA |

Example trap: "AI/ML" appears as Rel-18 (6.0.2.x), Rel-19 air interface (7.1),
Rel-20 PHY Ph2 (8.1) and Rel-20 mobility (8.3), and as a 6G common item
(9.3.3.2). The release cue is what disambiguates.

## Sub-item conventions
Most work items repeat the same numbered sub-structure. Route the *kind* of
contribution to the matching sub-item:

- **`.0` In-principle agreed CRs** — change requests already agreed in principle.
- **`.1` Organizational** — work plan, session planning, way forward, scope,
  status, chair's notes. Anything meta rather than technical.
- **`.2` Corrections / Essential corrections** — bug fixes and CRs against the
  feature. Use this for "correction", "essential correction", "CR to 38.xxx"
  unless a more specific correction sub-item exists (e.g. `.3` User plane).
- Technical sub-items (e.g. `8.1.2 LCM for two-sided model`,
  `8.3.2 RRM measurement prediction`) — the substance of a study/WI. Prefer these
  when the input describes an actual technical topic.

## Acronym expansion
| Acronym | Meaning |
|---|---|
| LCM | Life Cycle Management (of AI/ML models) |
| AI/ML | Artificial Intelligence / Machine Learning |
| PHY | Physical layer |
| NES | Network Energy Saving |
| LP-WUS / WUR | Low-Power Wake-Up Signal / Wake-Up Receiver |
| LTM | L1/L2-Triggered Mobility |
| SBFD | Sub-band Full Duplex |
| NTN | Non-Terrestrial Network |
| IoT NTN | Internet-of-Things over NTN |
| MIMO | Multiple-Input Multiple-Output |
| XR | Extended Reality (AR/VR/MR) |
| SON/MDT | Self-Organizing Networks / Minimization of Drive Tests |
| RRM | Radio Resource Management |
| MRO | Mobility Robustness Optimization |
| RACH | Random Access Channel |
| IAB | Integrated Access and Backhaul |
| UAV | Uncrewed Aerial Vehicle |
| IDC | In-Device Coexistence |
| RedCap | Reduced-Capability NR devices |
| A-GNSS | Assisted Global Navigation Satellite System |
| SPS | Standard Positioning Service (NavIC/GNSS context) |
| QoE | Quality of Experience |
| MBS | Multicast/Broadcast Services |
| MR-DC / EN-DC | Multi-Radio / E-UTRA-NR Dual Connectivity |
| TEI | Technical Enhancements and Improvements (release-tagged: TEI18/19) |
| ISAC | Integrated Sensing and Communication |
| CR | Change Request |
| HO | Handover |
