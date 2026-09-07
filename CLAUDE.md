# Job Application Pipeline - contributor notes

This file is for humans browsing the repository. Claude Code plugins don't load a
root-level `CLAUDE.md` as runtime context, so the actual guardrail Claude follows at
runtime lives in [skills/pipeline-safety/SKILL.md](skills/pipeline-safety/SKILL.md) -
read that file for the authoritative rules (never submit an application, read-only
job-discovery tools only, no credentials, keep every CV/cover-letter claim grounded in
the candidate's own data, never commit candidate data to this repo).

If you're adding a new command or skill to this plugin, make sure it's consistent with
that skill before opening a PR.
