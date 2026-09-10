---
description: Build or extend your experience knowledge base through an adaptive, resumable interview.
---

# /js-interview

Build `candidate/experience.json` - the knowledge base every later command (templates,
scoring, generated CVs and cover letters) depends on. This is a real interview in the
"get to know you" sense, not a job interview and not a rehearsal for one: the goal is
purely to understand and quantify what the candidate has actually done. See
`schemas/experience.schema.json` for the exact shape of the file this command writes.

## Prerequisites

Read `~/.job-application-pipeline/config.json` for `data_root`. If it doesn't exist,
tell the candidate to run `/js-setup` first, and stop.

## Step 0: figure out which mode this run is in

Check whether `<data_root>/candidate/experience.json` exists.

- **Doesn't exist** -> fresh start (below).
- **Exists, `meta.status` is `"in_progress"`** -> resume: summarize which experiences
  are already in `meta.sections_covered` and which aren't, whether the soft-skills
  pass is done (its own entry in `sections_covered`, `"soft-skills-pass"` - not tied
  to any one experience), then ask whether to continue in order or jump to a specific
  one.
- **Exists, `meta.status` is `"complete"`** -> ask whether the candidate wants to add
  a new experience that isn't in the file yet, or revisit/expand an existing one.
  Either way, go through the interview loop below for just that one experience, then
  re-save with `meta.status` still `"complete"`.

## Fresh start

### Step 1 — read everything they've given you

Look in `<data_root>/source-documents/`. The candidate is asked to drop **all** their
CVs and cover letters there, not just one, because people write different experiences
into different CVs depending on the job they were chasing. Reading them all is the
difference between starting from what they have and starting from whichever file they
happened to mention.

- **Readable**: `.docx` (via `python-docx`), `.txt`, `.md`.
- **Not readable here**: `.pdf`. Say so by name and ask for a re-save as `.docx` or a
  paste. **Never silently skip a file** - the candidate put it there believing it
  would be used, and a quietly ignored CV is the worst outcome of this whole step.
- Classify each document as a CV or a cover letter **by its content, not its
  filename**.
- If the folder is empty, explain where to put documents and offer to wait. Don't
  block permanently: someone may genuinely have no CV, and the interview can run from
  nothing.

Say what you read, in a line: how many CVs, how many cover letters, anything skipped.

### Step 2 — union the experiences, and record where each came from

Build one skeleton from **all** the CVs together:

- An experience appearing in any CV gets an entry. One appearing in several gets
  merged into a single entry, not duplicated.
- Give each a stable id (`exp-001`, ...), with title, organization, type and period.
  Leave `skills` empty - the interview fills those.
- Set `source_documents` on each entry: which files it came from. An experience that
  appears on only one CV is a signal worth keeping - they judged it irrelevant for
  the others - and it helps later tailoring decide what to include for a given job.

### Step 3 — note the conflicts, but don't ask yet

Several CVs will disagree. Sort the disagreements:

- **Material** - things that cannot both be true: dates, job titles, employer names,
  quantified results, qualification dates. Record these and **raise each one during
  that experience's turn in the interview loop**, not as a batch now. A wall of
  contradictions before the interview has even started is a bad opening, and the
  context needed to resolve one arrives when you're discussing that role anyway.
- **Not material** - wording, emphasis, ordering, which bullets a given CV included,
  formatting. Merge silently; there is nothing to resolve.

When you do raise one, be neutral about it. Two CVs disagreeing is normal and usually
means one was written quickly, not that anyone was being careless.

### Step 4 — identity and writing style

Extract identity (name, email, phone, location, links) from the most complete source.
Don't ask unless something is missing or the sources disagree.

Then extract their **writing style** and save it to
`<data_root>/candidate/writing-style.json`, per `schemas/writing-style.schema.json`.
This is what later stops generated bullets and cover letters reading as generic
business prose. CVs give you bullet style; cover letters give you their prose voice,
which matters more and is the only sample of it you will get.

Do not show this file to the candidate or ask them to confirm it - it is stored for
later commands to use, not a step to sit through.

**Every trait needs a quote behind it.** An invented style trait produces text that is
confidently wrong, which is worse than writing plainly. If the sample is thin - one
short CV, no letters - say so in `notes` so later commands lean on it lightly.

The `avoid` list is the one that does the most work: the words and constructions
absent from their writing that a generator reaches for by default. Sounding like
someone is mostly a matter of not writing "spearheaded".

### Step 5 — write the file and begin

Write the initial `experience.json`: `meta.status` = `"in_progress"`,
`meta.sections_covered` = `[]`, `identity` filled in, `axes` = `[]`, `experiences` =
the union skeleton. **Write any path with forward slashes** - see
`skills/pipeline-safety/SKILL.md`.

Then tell them what you found and start the loop with the first experience - e.g.
"Across your three CVs I found 9 things, four of which only appear on one of them.
I'll go through each to really understand it. We can stop anytime and pick up later."

## The interview loop (run once per experience)

Ask one thing at a time - never a wall of questions in a single message.

0. **Resolve any conflict recorded for this experience** (Step 3 above) before going
   further, while the context is in front of both of you. "Your 2023 CV has this
   ending in June and the other says September - which is right?" One question, no
   fuss, then correct the entry and move on.
1. **Start broad.** "Tell me about your work as [title] at [organization]. What were
   you responsible for day to day?"
2. **Probe specifics.** Tools/technologies/methods used, notable outcomes or metrics,
   team size and collaboration, problems solved.
3. **Help them remember what they'd otherwise skip.** Ask open, non-leading questions
   that broaden recall without suggesting specific skills the candidate hasn't named
   themselves - e.g. "Was there anything you did occasionally, or that supported the
   main work, that isn't obvious just from the title?" or "Did this involve any
   documentation, mentoring, cross-team coordination, or process work you haven't
   mentioned?" This is the most important part of the interview - most people
   undersell what they've actually done until asked this way.

   Also reason specifically about this experience's **profession**, not just its job
   title, and ask about what's commonly adjacent to it - people often pick up real
   skills that never make it onto a CV because they're not the role's core focus. A
   mechanical engineer often ends up doing some scripting, CAD automation, or data
   analysis; a teacher often ends up doing project management or public speaking
   outside the classroom; and so on for whatever field this experience is actually
   in. Ask an open question about the specific adjacent skill(s) you'd expect for
   this field ("People doing [this kind of work] often end up doing some
   [adjacent skill] too - has that come up for you?") rather than a generic "anything
   else?" This is still a memory-jogging prompt, not an assumption - if the candidate
   says no, drop it.
4. **Quantify each distinct skill that comes up:**
   - How long did they do this (duration)?
   - How often, or how many times (frequency or a repetition count)?
   - A 1-10 self-rated confidence: "On a scale of 1 to 10, how confident do you feel
     about [skill]?"
   - One concrete, specific detail that makes it defensible in an interview later (the
     `evidence` field) - not a generic restatement of the skill name.
5. **Assign an axis.** Check the existing `axes` array for a reasonable fit first.
   Only create a new axis if nothing existing fits, and keep the total count small
   (roughly 5-10) - broad, role-relevant groupings ("Backend Development", "Team
   Leadership", "Data Analysis") work better than one axis per tool. New axes start
   with `weight: 0` - that gets set later in `/js-preferences`.
6. **Link it to the same skill elsewhere, if it is the same skill.** Before writing
   `skill_key`, check every skill already recorded in *any* experience so far - not
   just this one - for something that's genuinely the same underlying skill, even if
   it's worded differently (e.g. "Gazebo simulation" in one job and "physics
   simulation tuning in Gazebo" in another are the same skill in different words). If
   you find a real match: say so to the candidate ("You mentioned Gazebo before, at
   [that experience] - does this deepen that, or about the same level?"), then give
   this new entry the *same* `skill_key` as the earlier one. Still write a full new
   entry for this experience - its own duration/frequency/evidence/confidence, since
   the context is genuinely different - just linked by the shared key. If there's no
   real match, invent a new `skill_key`: lowercase, hyphenated, naming the underlying
   skill concept (e.g. `cad-mechanical-design`), not the exact wording of `name`.
   Don't force a link that isn't real - a surface-level word match isn't the same
   skill (ROS1 and ROS2 are related but distinct; don't merge them just because both
   start with "ROS").
7. **Save before moving on.** Update `experience.json` with this experience's skills,
   add its id to `meta.sections_covered`, update `meta.last_updated`, and write the
   file now - not only once at the very end. This is what makes the interview
   resumable if the session ends partway through.
8. **Never invent or embellish.** If the CV states something vague, ask the candidate
   to clarify rather than assuming what it means. Every `evidence` string must be
   something the candidate actually said. If they say "I don't remember" or "not
   really," it's fine for that skill entry to simply not exist - do not fabricate one
   on their behalf.

## Soft skills

Run this once, after every experience from the CV has been through the loop above and
before wrapping up. Soft skills are consistently undersold if nobody asks about them
directly, and they deserve the same rigor as a technical skill, not a vague
self-assessment.

1. Go through these one at a time, skipping any that clearly don't apply given what's
   already come up: communication, leadership/mentoring, teamwork and collaboration,
   problem-solving under pressure, adaptability to change, conflict resolution, time
   management/prioritization, negotiation.
2. For each one the candidate says they have real experience with, ask for one
   concrete, specific example - a real situation, not a general claim: "Tell me about
   a time you had to [resolve a disagreement / lead through ambiguity / adapt to a
   sudden change]." That example is the `evidence` field, exactly like a hard skill -
   a soft-skill claim with no real example behind it is exactly what this pipeline
   exists to keep off a CV, so if they can't come up with one, don't record it.
3. Quantify it the same way as any other skill: how often this comes up, and a 1-10
   confidence rating.
4. Attach each confirmed soft skill to whichever existing experience entry its
   example actually happened in. If an example doesn't clearly belong to one
   experience (e.g. "I've always been like this, across every job"), create one
   shared experience entry, `type: "other"`, titled "Soft skills," to hold those.
5. Assign an axis and a `skill_key` the same way as any hard skill (steps 5 and 6 of
   the loop above) - soft skills often warrant their own axis or two (e.g.
   "Leadership & Communication") rather than being folded into a technical one, and
   are especially likely to recur across several experiences (e.g. leadership
   examples from more than one job) - link them by `skill_key` when they're genuinely
   the same underlying skill.
6. Save after this section the same way as after each experience in the loop, adding
   the literal string `"soft-skills-pass"` to `meta.sections_covered` so a resumed
   session knows this section is already done and doesn't repeat it.

## Wrapping up

Once every experience from the CV has been through the loop, and soft skills are
covered:

1. Ask if there's anything else worth adding that isn't on the CV - side projects,
   volunteer work, self-taught skills, open source contributions. Also ask, stepping
   back from specific roles: are there broader skills common in their field that they
   have real experience with but that haven't come up yet (the profession-adjacent
   angle from the interview loop, asked once more at the whole-career level as a
   final catch-all)? Run the interview loop for each thing they mention.
2. Set `meta.status` to `"complete"` and save.
3. Tell the candidate their knowledge base is built, briefly summarize the axes that
   emerged, and that the next step is `/js-preferences`.

## Pacing

This is meant to be thorough, not fast, and may reasonably span multiple sessions.
Let the candidate's answers set the pace. The value of this command is entirely in
how well it helps someone recall and quantify things they'd otherwise forget to
mention - don't rush past step 3 of the interview loop.
