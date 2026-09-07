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

1. Ask for the candidate's CV - a file path, or they can paste the text directly.
   Read it.
2. Extract identity fields (name, email, phone, location, links such as LinkedIn) from
   the CV text into an `identity` object. Don't ask about these unless something
   important is missing or ambiguous.
3. Extract a skeleton list of experiences (roles, projects, education, certifications)
   from the CV: title, organization, type, and period for each, in the order they
   appear. Give each a stable id (`exp-001`, `exp-002`, ...). Leave `skills` empty for
   now - that's what the interview fills in.
4. Write the initial `experience.json`: `meta.status` = `"in_progress"`,
   `meta.sections_covered` = `[]`, `identity` filled in, `axes` = `[]`, `experiences` =
   the skeleton above. **Write any path (e.g. `meta.source_cv_path`) with forward
   slashes** - see `skills/pipeline-safety/SKILL.md`.
5. Tell the candidate what you found (e.g. "I found 6 things on your CV: ... - I'll go
   through each one to really understand it. We can stop anytime and pick back up
   later."), then start the interview loop with the first experience.

## The interview loop (run once per experience)

Ask one thing at a time - never a wall of questions in a single message.

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
