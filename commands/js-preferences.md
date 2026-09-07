---
description: Set your job-search needs and priorities - location, must-not-haves, search terms, and how to weigh your skills against job postings.
---

# /js-preferences

Build `candidate/preferences.json` and `candidate/scoring-config.json`. Together with
`candidate/experience.json`'s `axes`, these three files are what `/js-scan` will later
score job postings against.

## Prerequisites

1. Read `~/.job-application-pipeline/config.json` for `data_root`. If it doesn't exist,
   tell the candidate to run `/js-setup` first, and stop.
2. Read `<data_root>/candidate/experience.json`.
   - Doesn't exist -> tell the candidate to run `/js-interview` first, and stop. The
     skill-priority tool below needs real axes to weigh; there's nothing to build yet.
   - Exists but `meta.status` is `"in_progress"` -> mention that the interview isn't
     finished, so some skill axes might still be missing, but it's fine to set
     preferences now and re-run the priority-weighting step later once more axes
     exist. Don't block on this - just say it once.

## Part 1: the questions (ask one at a time)

If `candidate/preferences.json` already exists, show the candidate their current
answers first and ask whether they want to update anything, rather than re-asking
everything from scratch.

Cover, in plain conversational language, not as a form:

1. **Location** - where they're based (for commute-distance links later).
2. **Work mode** - remote / hybrid / onsite, and any preference among them.
3. **Commute stance** - how far/long they're realistically willing to go for an
   onsite or hybrid role, in their own words (this stays a free-text note, not a
   computed distance - see the Key Decisions in the project's plan for why).
4. **Must-not-haves** - dealbreakers a posting should be flagged for (e.g. "no
   weekend on-call", "no more than occasional travel").
5. **Target search terms** - the job titles/keywords that will later define what
   `/js-scan` even searches for (e.g. "Robotics Engineer", "Controls Engineer"). This
   is the search *scope*, separate from job-fit scoring - anything outside these
   terms won't be fetched at all, regardless of how good a fit it might be.
6. **Language rule** - default is "match the job posting's language, ask me if it's
   ambiguous." Ask if they want a custom override instead (e.g. "always do both
   languages" or "postings in country X are always in French"), and only store a
   `custom_language_rule` if they give one.

Write `candidate/preferences.json` with these fields:
```json
{
  "location": "...",
  "work_mode": ["remote", "hybrid"],
  "commute_note": "...",
  "must_not_haves": ["..."],
  "target_search_terms": ["...", "..."],
  "language_rule": "match-posting",
  "custom_language_rule": null
}
```

## Part 2: priority weighting and scoring config

1. Read the `axes` array from `candidate/experience.json` (id, label, current
   `weight`). Each axis's `weight` doubles as its last-set priority score (0-10) -
   default any axis still at `0` (never yet set) to `5`, a neutral starting point,
   rather than carrying the literal 0 forward - `0` on this tool means "doesn't
   matter to me at all," which is different from "not decided yet." If
   `candidate/scoring-config.json` already exists, read it too, so the tool can open
   pre-filled instead of reset to defaults:
   - `match_style` (0-100) = `round(coverage_weight * 100)`
   - `selectivity` = `"picky"` if `prioritized_threshold >= 70`, `"generous"` if
     `prioritized_threshold <= 50`, else `"balanced"`
2. Copy `templates/priority-weighting-template.html` to
   `<data_root>/candidate/priority-weighting.html`, replacing everything between the
   `JAP_TEMPLATE_DATA_START` / `JAP_TEMPLATE_DATA_END` markers with the real
   `TEMPLATE_DATA` object, plus `matchStyle` and `selectivity` from step 1 (or the
   template's own defaults, 50 and `"balanced"`, if there's no existing scoring
   config). Leave everything else in the template untouched.

   **The field is `score`, not `weight`.** `experience.json` calls this number
   `weight`; the tool expects `score`. Rename it when you seed, and make sure the
   value is on the 0-10 scale:
   ```js
   const TEMPLATE_DATA = {
     axes: [
       { id: "axis-robotics", label: "Robotics & Simulation", score: 9 },
       { id: "axis-control", label: "Control & Estimation", score: 6 }
     ],
     matchStyle: 50,
     selectivity: "balanced",
   };
   ```
   (The template does defend itself - it accepts `weight` as a fallback and rescales
   anything above 10 down proportionally - but don't rely on that; seed it correctly.)
3. Tell the candidate to open `<data_root>/candidate/priority-weighting.html`
   (double-clicking it works - no server needed), adjust things, click Save, and then
   tell you when they're done.
4. Once they confirm, look for `job-search-priorities.json` in `<data_root>/inbox/`
   - **only there, never their real Downloads folder** (see
   `skills/pipeline-safety/SKILL.md`). If it isn't there, remind them their browser's
   download location should point at the inbox, or they can move the file across by
   hand; don't go looking for it elsewhere. If several copies exist (browsers add a
   `(2)` suffix rather than overwriting), use the most recently modified one and say
   which. Read it - it has this shape:
   ```json
   { "axis_scores": { "<axis id>": 0-10, ... }, "match_style": 0-100, "selectivity": "picky|balanced|generous" }
   ```
5. Apply it:
   - Update `candidate/experience.json`: for each id in `axis_scores`, set that
     axis's `weight` in the `axes` array to the new score as-is (no rescaling - these
     are relative weights the scoring algorithm uses multiplicatively, not
     percentages that need to sum to anything). Touch nothing else in the file - not
     `experiences`, not `identity`, not `meta`.
   - Write `candidate/scoring-config.json`:
     ```json
     {
       "coverage_weight": <match_style / 100>,
       "depth_weight": <1 - coverage_weight>,
       "required_multiplier": 2,
       "nice_to_have_multiplier": 1,
       "prioritized_threshold": <75 if picky, 60 if balanced, 45 if generous>,
       "tier_bands": [
         { "label": "Strong", "min": 80 },
         { "label": "Possible", "min": 50 },
         { "label": "Weak", "min": 0 }
       ]
     }
     ```
6. Confirm to the candidate what was saved, and that it's safe to delete the
   downloaded file now. Recommend `/js-status` to see what's next.

If the candidate says they clicked Save but no file turns up after a reasonable
search, don't guess or fabricate values - ask them to check where their browser saved
it, or to try clicking Save again.
