---
description: One-time setup - choose where your private job-search data lives, then create the folder structure.
---

# /js-setup

Set up (or reconfigure) the private data folder for the Job Application Pipeline.
Nothing this command creates ever lives inside this plugin's own install directory or
repository - it all goes in a folder the candidate chooses, entirely on their own
machine.

## Steps

1. Check whether `~/.job-application-pipeline/config.json` already exists.
   - If it exists, read it, show the candidate the current `data_root`, and ask
     whether they want to keep it or point to a different folder. If they want to
     keep it, just confirm the folder tree below is intact (creating any missing
     pieces) and stop here.
2. Determine the data-root path:
   - If this command was invoked with an argument (`$ARGUMENTS`), treat that as the
     path directly - no need to ask.
   - Otherwise, ask the candidate for a path, suggesting a sensible default such as
     `~/job-search-data`, and explain in one sentence that this folder is where all
     of their personal data will live, separate from the plugin's install location
     and never shared publicly.
3. Create this folder structure under the chosen data-root (create only what's
   missing, never overwrite existing files):
   ```
   <data-root>/
     config.json
     candidate/
     source-documents/  <- the candidate puts their CVs and cover letters here
     templates/
     scans/
     inbox/             <- where the browser saves files back to
     .tools/            <- scratch venv for docx rendering; safe to delete
   ```

   Write a short `README.txt` inside `source-documents/` saying what belongs there:
   every CV and cover letter they have, `.docx` or plain text (PDFs can't be read),
   and that more is better because different CVs usually carry different experiences.
   Someone who opens an empty folder in Explorer has nothing else to go on.
   Write `config.json` only if it doesn't already exist, with this content:
   ```json
   {
     "data_root": "<absolute path>",
     "created": "<today's date, ISO 8601>",
     "job_sites": [],
     "scan_history": []
   }
   ```
   **Normalize `<absolute path>` to forward slashes before writing it** (e.g.
   `C:/Users/name/job-search-data`, not `C:\Users\name\job-search-data`) - see
   `skills/pipeline-safety/SKILL.md` for why a raw Windows path breaks JSON.
4. Write (or overwrite) the pointer file at `~/.job-application-pipeline/config.json`:
   ```json
   { "data_root": "<absolute path>" }
   ```
   Same forward-slash normalization as step 3. This is how every other command in this
   plugin finds the candidate's data from any terminal or session, regardless of
   current working directory.
5. Explain the inbox, once, in plain language. Some pages in this pipeline are
   interactive HTML the candidate edits in their browser (setting skill priorities,
   flagging which jobs are worth applying to) and those pages save by downloading a
   small file. A local HTML page cannot choose where a download goes, so ask the
   candidate to point their browser's download location at `<data-root>/inbox/`
   once - in Chrome or Edge: Settings -> Downloads -> Location -> Change.
   Say why it matters: it means their saved files land where the pipeline can find
   them, and that this plugin only ever reads that one folder, never their real
   Downloads folder.
   If they would rather not change the setting, tell them they can simply move the
   downloaded file into `<data-root>/inbox/` by hand each time - it works the same,
   it's just an extra step.
6. Confirm success to the candidate in plain language: where their data folder is, and
   what happens next.

   If they arrived here from `/js-guide`, just hand back to it - don't send them off
   to type something. If they ran `/js-setup` directly, tell them `/js-guide` will
   walk them through the rest and is the only command they need to remember, with
   `/js-status` as a quick checklist if they prefer driving themselves.

## Notes for whoever implements later phases

This command only creates the skeleton. It does not populate
`candidate/experience.json`, `candidate/preferences.json`, or
`candidate/scoring-config.json` - those are written by later commands
(`/js-interview`, `/js-preferences`) once they exist. `/js-status` is the command that
tells the candidate what's still missing.
