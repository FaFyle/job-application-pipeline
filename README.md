# Job Application Pipeline

A Claude Code plugin that automates job-application prep:

1. A one-time interview captures your quantified experience (what you did, for how
   long, how often, how confident you are in it).
2. A one-time template design produces a CV, cover letter, and per-application prep
   report you like.
3. A recurring, schedulable job search finds postings, scores how well each one fits
   your profile against priorities you set, and auto-drafts a tailored CV, cover
   letter, and prep briefing for the ones worth pursuing.

**This plugin never submits an application.** Job discovery uses read-only
search/fetch tools only — no browser automation, no credentials, no form-filling. It
stops at producing documents; the application itself is up to you.

## Safety

See [CLAUDE.md](CLAUDE.md) for the guardrail this plugin's skills are built under.

## Your data stays yours

This repository contains only plugin code: commands and generic, anonymized starter
templates. Nothing about you or your job search is ever stored or committed here.
Once installed, all of your data (CV, generated applications, preferences) lives in a
private folder on your own machine, chosen when you run `/js-setup`.

## Install

```
claude plugin marketplace add <path-or-url-to-this-repo>
claude plugin install job-application-pipeline@job-application-pipeline-marketplace
```

## Getting started

Run `/js-setup` once to choose where your private data folder lives, then run
`/js-status` any time — it looks at what you've done so far and tells you what to do
next.

## Something wrong, or an idea?

Run `/js-feedback`. It asks what happened, checks the obvious causes first (an
out-of-date install explains a surprising amount), and if there's a real problem it
writes a report you can send on or paste into a GitHub issue.

It never reads anything in your data folder — the report contains what you type and
the plugin version, nothing else — so you can share it without checking what's in it.

## Status

Under active, incremental development. See the project's implementation plan for the
current build phase.
