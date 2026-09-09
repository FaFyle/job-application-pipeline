---
description: Report a bug, request a change, or suggest an improvement - and get it written up properly.
allowed-tools: Read, Write, Bash
---

# /js-feedback

Turn "this didn't work" into something the plugin's author can act on.

This runs inside the session where the problem happened, which is the whole point: you
can check a claim rather than transcribe it. Often the best outcome is that no report
gets written at all, because the thing was a misunderstanding or a stale install.

Usable at any time. It is deliberately outside the pipeline's flow.

## The one hard rule: never read the candidate's data folder

**Do not open anything under `candidate/`, `scans/`, `templates/` or `inbox/`.** Not
to "check the file they mentioned", not to confirm a detail, not even when the person
offers. The report contains what they typed, plus the plugin version. Nothing else.

The reason is the destination: this file may be pasted into a *public* GitHub issue,
and their data folder holds CVs, employer names, contact details and job applications.
This plugin's promise is that that material never leaves their machine, and a helpful
diagnostic dump would quietly break it. Because nothing personal is ever collected,
the finished file is safe to paste anywhere without anyone having to vet it first.

Reading `~/.job-application-pipeline/config.json` to find where to save the report is
fine. Reading what is inside that folder is not.

If a detail from their data would genuinely help, **ask them to describe or paste it**
and let them decide what to share.

## Step 1: listen

Let them describe it in their own words first. Don't open with a form. Someone filing
feedback is usually already frustrated, and an interrogation makes it worse.

## Step 2: check the version before treating anything as a bug

Run `claude plugin list` and compare the installed version against the marketplace
source. Two things to establish:

- Are they on the latest version?
- Did this session start *before* the last update? Plugin updates only take effect in
  a new session, so a command can be missing or behave like an older build even after
  updating.

If either is off, that is the likely explanation. Say so, ask them to restart and try
again, and don't write a report yet. This is the highest-yield check available - a
large share of problems in this project's own history were exactly this.

## Step 3: work out what kind of thing this actually is

Four outcomes, and they need different handling:

- **A misunderstanding.** The thing works as intended and was misread. Explain what it
  actually does and why, confirm that resolves it, and **write no file** - say plainly
  that nothing was filed, and what the answer was.
- **A bug.** It genuinely does not do what it says.
- **Works as designed, but the design is wrong.** This feels identical to a bug from
  the outside and is completely different from the inside: there is no defect to find.
  Record it as a change request and say that's what you're doing, so the author isn't
  sent hunting for broken code.
- **An improvement or new idea.** Nothing is wrong; something could be better.

## Step 4: push for specifics, kindly

"It didn't work" is not a report. Get the actual command they ran, what appeared, and
what they expected instead. Enough that someone else could reproduce it.

When what they describe conflicts with what you can see, say so concretely and without
implying they're wrong or careless:

> "The version installed here is 0.9.0, and `/js-generate` only arrived in 0.11.0 -
> does that match what you were running?"

Ask one thing at a time. Stop asking as soon as you have enough; completeness is not
worth exhausting them for.

**For a change request or improvement, dig for the problem behind the solution.**
People naturally propose fixes. If the report captures only the proposed fix, the
author builds the wrong thing correctly. Ask what they were trying to achieve and what
made it hard.

## Step 5: write it up

Write to `<data_root>/feedback/YYYY-MM-DD-<short-slug>.md`. If `/js-setup` has never
run, fall back to the user's home directory and tell them where it went.

Formatted to paste straight into a GitHub issue: headings that render, no preamble.

For a **bug**:

```markdown
# <one-line summary>

**Type:** Bug
**Plugin version:** <version>

## What I was doing
## Steps to reproduce
1.
2.
## What happened
## What I expected
## How often
## Impact

---
### Checked during this conversation
- <e.g. version is current and the session was restarted after updating>
- <e.g. ruled out: this is not the inbox-not-configured case>
```

For a **change request or improvement**:

```markdown
# <one-line summary>

**Type:** Change request
**Plugin version:** <version>

## The problem this causes
## How it behaves today
## What I'd like instead
## Why it matters
## Anything already tried

---
### Checked during this conversation
- <what was ruled out>
```

The "checked during this conversation" section matters: it shows the author the triage
that already happened so he doesn't repeat it. Keep it factual and short.

Write only what the person actually said. Do not invent reproduction steps, infer an
impact they didn't describe, or smooth a vague answer into a confident one - a
plausible-sounding report that misstates the problem is worse than a thin accurate
one. Where something is unknown, write "not sure" and leave it.

## Step 6: hand it over

1. **Print the whole file in the chat**, so it can be copied straight into an issue or
   a message without opening anything.
2. Say where it was saved.
3. Offer to open the containing folder, for anyone who'd rather drag the file into a
   chat window. On Windows that's `explorer <folder>`; macOS `open`; Linux
   `xdg-open`.
