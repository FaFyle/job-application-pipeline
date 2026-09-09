# Where the candidate is, and what comes next

The single source of truth for reading pipeline state and deciding the next step.
`/js-status` reads this and prints a checklist; `/js-guide` reads it and acts on the
verdict without printing one. Neither carries its own copy.

**Adding a phase means editing this file, and only this file.**

## Reading the state

1. `~/.job-application-pipeline/config.json` -> `data_root`. Missing means setup has
   never run, and nothing below applies.
2. `<data_root>/config.json` — pipeline-level state: confirmed job sites, scan history.
3. Then check for these, by presence rather than full validity:

| What | Where | Notes |
|---|---|---|
| Knowledge base | `candidate/experience.json` | Read `meta.status`. `"in_progress"` is a **third state**, distinct from missing and from `"complete"` — the interview is resumable and saves after every experience. |
| Preferences | `candidate/preferences.json` | Needs, priorities, search terms |
| Scoring config | `candidate/scoring-config.json` | Job-fit tuning |
| Templates | `templates/cv-template.docx`, `cover-letter-template.docx`, `prep-report-template.html` | The CV is a `.docx`; an older `cv-template.html` is stale and does not count |
| Scans | any folder under `scans/` | At least one completed search |
| Generated applications | `scans/<date>/applications/*/cv.docx` | A prioritized job without one has not been generated yet |
| Unapplied saves | `<data_root>/inbox/` | Files saved from an interactive page that nothing has picked up |

## The ladder

Take the first that applies:

1. **No pointer config** -> `/js-setup`. Nothing else can run without it.
2. **`experience.json` missing, or `meta.status` is `"in_progress"`** -> `/js-interview`.
   If in progress, say it picks up where it left off rather than starting over.
3. **`preferences.json` or `scoring-config.json` missing** -> `/js-preferences`.
4. **Templates missing** -> `/js-templates`.
5. **No scans yet** -> `/js-scan`.
6. **A scan has prioritized jobs with no `cv.docx`** -> `/js-generate`.
7. **Everything present** -> set up. `/js-scan` can be re-run any time for new jobs.

## Checked at every stage, independent of the ladder

- **The inbox.** If `<data_root>/inbox/` holds anything, mention it and point at
  `/js-apply` — someone who saved from a page and closed it has no other way to
  discover the file was never picked up. This is not a ladder step; it can be true at
  any point.
- **Commands that don't exist yet.** This plugin is built one phase at a time. If the
  recommended command isn't in the installed version, say so plainly ("not built yet")
  rather than trying to invoke it.
