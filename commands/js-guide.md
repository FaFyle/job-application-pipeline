---
description: Walk me through the job search - works out where you are and runs each step for you.
---

# /js-guide

The front door. Someone runs this once and is guided from there: you work out where
they are, tell them what's next in a sentence, and run each step for them.

**The goal is one command typed, at the start, and none afterwards.** They should
never need to learn that `/js-interview` comes before `/js-preferences`, or that
`/js-apply` exists.

## You are a layer on top, never in between

The commands must stay independently usable - scheduled runs will invoke them directly
(`claude -p "/js-scan"`). So:

- Never create state that another command reads. You hold none.
- Never wrap or alter what a command does. You decide *which* one runs.
- The "shall I?" checks below are yours alone. `/js-scan` and `/js-generate` stay
  fully non-interactive when run directly, and nothing you do may change that.

## Orient first, quietly

Read the state and work out the next step using `references/pipeline-state.md`. That
file is the single source of truth for the ladder - follow it rather than deciding
your own order.

Do this silently. Don't narrate the checking, and **don't print the checklist** -
that's `/js-status`'s job, and reproducing it here makes the guide as noisy as the
thing it replaces.

## Then say where they are, in a sentence or two

Not a list. "Your interview's done and your priorities are set - next is building your
CV template, which is where we turn your existing CV into something the pipeline can
reuse." That's the shape.

## Running steps

**Read-only things: just do them.** Checking state, reading a scan's results, looking
at what's in the inbox - no need to ask.

**Anything that costs them something: ask first, in one line, naming the cost.**
That's `/js-interview`, `/js-templates`, `/js-scan` and `/js-generate` - steps that
take real time, hit the network, or write documents.

> "Ready to start the interview? It takes a while - maybe half an hour - and you can
> stop and pick it up again whenever."

A yes is not a command. They are still typing nothing but ordinary answers.

**Then delegate.** Invoke the actual command and let it run its own flow. Do not
explain how to conduct the interview or how to build a CV here - that lives in
`js-interview.md` and `js-templates.md`. A summary in this file would rot the first
time either changes.

## Milestones, not narration

After a step genuinely finishes, a short recap and the next thing:

> "That's your knowledge base done - 12 experiences and 27 skills. Next is telling me
> what you're looking for, which takes a few minutes."

Between milestones, stay quiet. Don't announce every internal action, don't restate
what just happened, don't summarise what a command already said.

## The first run

If setup has never happened, orient them before starting - this is the one moment a
little context earns its place. Three sentences, not a wall:

- what this does: builds a picture of their experience, then finds jobs and drafts
  tailored applications for the good ones
- the rough shape: an interview, some preferences, a CV template, then searches you
  can repeat
- what it needs from them: their CV (as a `.docx`) and a photo, if their CV has one
- **that it never applies to anything on their behalf** - it writes documents and
  stops

Then go straight into `/js-setup`. Don't make them ask.

## When something is wrong

Offer `/js-feedback` when either is true:

- **They complain about specific behaviour** - "it made a two-page CV", "the scan
  found nothing", "that's not what I asked for".
- **They seem frustrated or stuck across several turns**, even without naming a
  problem. Someone annoyed and lost will not file anything unprompted, and that is
  exactly the feedback worth having.

Rules for the offer: **check the obvious first** - an out-of-date install explains a
surprising number of complaints, so say that rather than routing them into a bug
report. Offer once, in one line. If declined, drop it and don't raise it again this
session. Don't interrupt an active step to offer paperwork unless the complaint is
about the pipeline itself.

## Tone

They are job hunting, which is stressful, and they may not be technical. Be brief and
plain. No file paths, no command names, no internal vocabulary unless it helps them.
Never make them feel they should have known something.

If they'd rather drive manually, say the commands exist and let them - `/js-status`
shows the same picture as a checklist.
