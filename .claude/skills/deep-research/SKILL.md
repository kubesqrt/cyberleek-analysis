---
name: deep-research
description: Exhaustive, multi-agent, fact-checked research on any question using the web. Use when the user asks for deep, in-depth, thorough or comprehensive research, a literature/market/technical review, or invokes /deep-research. Fans out parallel researcher agents, adversarially verifies key claims, loops on gaps, and delivers a cited report.
---

# Deep research

The user invoked this skill, which counts as opting in to multi-agent orchestration: run the Workflow tool as described below.

## 1. Scope (inline, before any agents)

- Restate the question in one sentence. If it is genuinely ambiguous in a way that changes the research (which market, which time window, which jurisdiction, what decision it feeds), ask the user up to 3 short questions with AskUserQuestion. Otherwise pick sensible defaults and state them.
- Pick depth: `max` if the user says exhaustive / no limits / tokens don't matter, else `standard`.
- Get today's date (`date -u +%F`) to pass in, since workflow scripts can't read the clock.

## 2. Run the workflow

Call Workflow with:

- `scriptPath`: the `workflow.js` file next to this SKILL.md (absolute path)
- `args`: `{ "question": "<restated question>", "context": "<user's goal, constraints, defaults you chose>", "today": "<YYYY-MM-DD>", "depth": "standard" | "max" }`

What it does:
1. **Plan**: orienting searches, then 6-14 non-overlapping sub-questions with concrete search angles.
2. **Research**: one agent per sub-question, extended web search, reads 6-10+ full sources, returns a claim ledger (claim + URL + verbatim quote + date + source type).
3. **Verify**: 2-3 independent skeptics per sub-question try to refute each key claim against independent sources. Majority vote decides confirmed / refuted / outdated / contested.
4. **Gaps**: a completeness critic proposes new sub-questions. This loops until nothing material is missing (max 3-4 rounds).
5. **Synthesize**: writes a report from the ledger only, with inline citations, confidence levels, disagreements and unknowns.

If it is interrupted, resume with `resumeFromRunId` and completed agents are reused from cache.

## 3. Deliver

- Spot-check: open 2-3 of the most load-bearing citations yourself and confirm they say what the report claims. Fix anything wrong.
- Publish the report as an Artifact (load `artifact-design` first) unless the user asked for chat or a file. Then give a 5-line summary in chat: the bottom line, overall confidence, the number of key claims confirmed out of the total, and any unresearched gaps the workflow returned.
- Don't hide weaknesses. If key claims were contested or gaps remained, say so.

## Without the Workflow tool

If Workflow isn't available, run the same phases by hand. Launch researchers in parallel with the Agent tool (one message, many calls), then verifier agents, then the gap critic, then write the report yourself, using the same source rules from `workflow.js`.
