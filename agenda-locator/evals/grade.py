#!/usr/bin/env python3
"""Grade eval answers: does the saved answer.md name the correct agenda number?"""
import os, re, json, sys

ITER = sys.argv[1] if len(sys.argv) > 1 else 'iteration-1'
BASE = os.path.join(os.path.dirname(__file__), ITER)

# expected agenda per eval id; '|' means either acceptable (ambiguous case)
EXPECT = {0: '8.1.2', 1: '7.1.2', 2: '8.3.2', 3: '7.5.2',
          4: '8.7.2', 5: '8.1.2', 6: '7.11.2', 7: '8.1.3|8.3.4'}
# traps: numbers that indicate a WRONG release/domain if presented as the answer
TRAP = {1: ['8.1.2', '8.3.2'], 2: ['7.1.2', '8.1.2'], 4: ['7.9.', '6.0.2.18']}


def num_tokens(text):
    return set(re.findall(r'\d+(?:\.\d+)+', text))


def grade_one(path, eid):
    if not os.path.exists(path):
        return {"found": False, "correct": False, "answer_nums": [], "note": "no answer.md"}
    text = open(path, encoding='utf-8', errors='ignore').read()
    nums = num_tokens(text)
    accepted = EXPECT[eid].split('|')
    correct = any(a in nums for a in accepted)
    return {"found": True, "correct": correct,
            "answer_nums": sorted(nums)[:12],
            "expected": EXPECT[eid]}


def main():
    results = {}
    for eid in EXPECT:
        for cfg in ('with_skill', 'without_skill'):
            p = os.path.join(BASE, f'eval-{eid}', cfg, 'outputs', 'answer.md')
            results[f'eval-{eid}-{cfg}'] = grade_one(p, eid)
    # summary
    for cfg in ('with_skill', 'without_skill'):
        rows = [(eid, results[f'eval-{eid}-{cfg}']) for eid in EXPECT]
        ok = sum(1 for _, r in rows if r['correct'])
        print(f"\n=== {cfg}: {ok}/{len(rows)} correct ===")
        for eid, r in rows:
            mark = 'OK ' if r['correct'] else ('-- ' if not r['found'] else 'XX ')
            print(f"  {mark} eval-{eid} expect {r.get('expected','?'):<12} found={r['answer_nums']}")
    json.dump(results, open(os.path.join(BASE, 'grading_summary.json'), 'w'), indent=2)
    print("\nwrote grading_summary.json")


if __name__ == '__main__':
    main()
