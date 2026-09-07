---
description: Orchestrator - shows what's been completed so far and what to do next.
---

# /js-status

Give the candidate a plain-language checklist of pipeline progress and a single clear
recommendation for what to run next. Do not assume technical knowledge - explain
things the way you would to someone who has never used Claude Code before.

## Steps

1. Read `~/.job-application-pipeline/config.json` for the pointer to `data_root`.
   - If this file doesn't exist, tell the candidate to run `/js-setup` first, and stop.
2. Read `<data_root>/config.json` for pipeline-level state (confirmed job sites, scan
   history).
3. Check for the presence (not full validity) of these files/folders and report each
   as done or missing:
   - `candidate/experience.json` - the knowledge base from the interview. If it
     exists, also read its `meta.status`: `"in_progress"` is a distinct state from
     missing entirely or `"complete"` - report it as "started, not finished yet"
     rather than lumping it in with either done or missing.
   - `candidate/preferences.json` - needs, priorities, search terms
   - `candidate/scoring-config.json` - job-fit scoring tuning
   - `templates/` containing a CV template, cover-letter template, and prep-report
     template
   - Any folder under `scans/` - at least one completed job search
4. Print a short, friendly status list (done vs. in-progress vs. missing), then
   recommend exactly one next command, in this priority order:
   1. `experience.json` missing or `meta.status` is `"in_progress"` -> recommend
      `/js-interview` (mention it'll pick up where it left off if already started)
   2. Missing `preferences.json` or `scoring-config.json` -> recommend `/js-preferences`
   3. Missing templates -> recommend `/js-templates`
   4. Everything above present, no scans yet -> recommend `/js-scan`
   5. Everything present -> tell them the pipeline is fully set up, and `/js-scan`
      can be re-run any time to search for new jobs.
5. If a command referenced above doesn't exist yet in the installed version of this
   plugin, say so plainly (e.g. "not built yet - that's a later phase") rather than
   trying to invoke it.

## Notes for whoever implements later phases

Step 5 exists because this plugin is being built one phase at a time. Update this
command's step 4 checklist as each new command/skill is built, so `/js-status` always
reflects what's actually available in the installed version.
