---
description: Apply whatever you saved from an interactive page - priority scores, or which jobs are worth applying to.
allowed-tools: Read, Write, Edit, Glob, Bash
---

# /js-apply

The interactive pages in this pipeline save by downloading a small file and telling
the candidate to come back here. This is the command that picks those files up.

Run it whenever they say they've saved something, and it will work out what they
saved rather than making them explain.

## Where to look

**Only `<data_root>/inbox/`.** Never the candidate's real Downloads folder - see
`skills/pipeline-safety/SKILL.md`. If the expected file isn't in the inbox, say so
and offer the two fixes: point the browser's download location at the inbox
(Settings -> Downloads -> Location), or move the file there by hand. Do not go
looking for it elsewhere.

If several copies exist (`job-search-priorities (2).json` and friends - browsers add
a suffix rather than overwriting), use the most recently modified one and tell the
candidate which, then offer to clear the older ones out.

## Prerequisites

Read `~/.job-application-pipeline/config.json` for `data_root`. Missing ->
`/js-setup`, stop.

## What each file means

### `job-search-priorities.json` - from the priority-weighting tool

```json
{ "axis_scores": { "<axis id>": 0-10 }, "match_style": 0-100, "selectivity": "picky|balanced|generous" }
```

- For each id in `axis_scores`, set that axis's `weight` in `candidate/experience.json`.
  **Write the score as-is - never rescale it to percentages.** These are relative
  0-10 priorities and job-fit scoring uses them multiplicatively, so only their ratios
  matter. Touch nothing else in that file.
- Write `candidate/scoring-config.json`: `coverage_weight` = `match_style / 100`,
  `depth_weight` = the remainder, `required_multiplier` 2, `nice_to_have_multiplier`
  1, `prioritized_threshold` 75/60/45 for picky/balanced/generous, and the standard
  tier bands.
- If an axis in the file no longer exists in `experience.json`, say so rather than
  creating it - it usually means the interview was re-run since.

### `scan-overrides.json` - from the scan dashboard

```json
{ "scan_date": "YYYY-MM-DD", "overrides": { "<job_id>": "forced_prioritized" | "forced_skipped" | null } }
```

- Find each `job_id` in `scans/<scan_date>/applications/*/fit-score.json` and set its
  `override`. `null` clears one, returning that job to whatever its score decides.
- These are deliberate decisions and must survive a re-scan: `/js-scan` preserves a
  non-null `override` rather than recomputing over it.
- A job newly forced to prioritized has no documents yet. Say how many are in that
  state and offer to run `/js-generate` for them - don't generate unasked, since it
  is slow and the candidate may have more flipping to do.

## After applying

1. Say plainly what changed - which axes moved, which jobs were flipped - so the
   candidate can see their edit took effect. A silent success is indistinguishable
   from a silent no-op.
2. Offer to delete the file from the inbox now it's applied, so the next run doesn't
   re-apply stale decisions.
3. If the inbox is empty, say so and name the pages that write to it, rather than
   reporting a vague failure.
