---
description: Quick status check - what's done, what's missing, and the one thing to do next.
---

# /js-status

Print a plain-language checklist of pipeline progress and name the single next step.

This is the quick, scriptable view. `/js-guide` is the conversational one that walks
someone through the whole thing and runs each step for them - point at it if the
person seems unsure what any of this is.

## Steps

1. Read the state and work out the next step exactly as described in
   `references/pipeline-state.md`. That file is the single source of truth for both
   the state table and the priority ladder - **do not keep a second copy of the order
   here**, or the two will drift as commands are added.
2. Print a short, friendly status list: done, in progress, and missing. Someone who
   has never used Claude Code should understand it - no jargon, no file paths unless
   they're useful.
3. Name exactly one recommended next command, and say in a few words what it does.
4. Mention anything sitting unapplied in the inbox, at any stage.
5. If the recommended command doesn't exist in the installed version yet, say so
   plainly rather than trying to invoke it.
