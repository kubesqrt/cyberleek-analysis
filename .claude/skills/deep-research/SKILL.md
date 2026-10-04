---
name: deep-research
description: Exhaustive, multi-agent, fact-checked research on any question or objective using the web and forums/communities. Use when the user asks for deep, in-depth, thorough or comprehensive research, a literature/market/technical review, or invokes /deep-research. Scouts, researcher trios, lead triage, deep-dive swarms on forum threads/tools/people/papers, full citation verification, director loop, parallel section writers, multi-pass review, and a very long cited report with appendices.
---

# Deep research

The user invoked this skill, which counts as opting in to multi-agent orchestration: run the Workflow tool as described below. A run uses hundreds of agents and can take a long time; that is intended.

## 1. Scope (inline, before any agents)

- Restate the question in one sentence. If the user has a goal ("I want to…", "help me find/choose/start…"), capture it separately as the `objective`; the report then contains ranked recommendations.
- If the question is genuinely ambiguous in a way that changes the research (which market, which time window, which jurisdiction, what decision it feeds), ask the user up to 3 short questions with AskUserQuestion. Otherwise pick sensible defaults and state them.
- **Separate examples from the target.** Users often give an example to show what they mean ("like X"), not to have X researched. For every concrete example in the request, decide whether it is the *subject* or an *illustration* of a broader category. If unclear, ask. For illustrations, write down the general category and which traits of the example matter, and pass them as `examples`. Never let the question collapse into "research X".
- Pick depth: `max` if the user says exhaustive / deep dive / no limits / tokens don't matter, else `standard`.
- Get today's date (`date -u +%F`); the script refuses to run without it.

## 2. Run the workflow

**Check concurrency first.** The Workflow tool runs at most `min(16, CPUs - 2)` agents at a time (`nproc` on Linux, `sysctl -n hw.ncpu` on macOS, `echo %NUMBER_OF_PROCESSORS%` on Windows). With 10+ CPUs use the Workflow tool as below. With fewer, use **orchestrator mode**: `dr.mjs` next to this file emits each phase's prompt files and absorbs agent JSON outputs; you launch one Agent per prompt file (all in one message, in parallel) with the instruction "Your full instructions are in <prompt path>. Read it first, then carry out the task exactly, including the OUTPUT CONTRACT." The command sequence is in the header comment of `dr.mjs` (`DR_RUN=<run dir> node dr.mjs <command>`); each command prints the prompt files to launch, and `absorb-*` commands print what is missing. Keep the run dir in the scratchpad or a `research/` folder.

Call Workflow with:

- `scriptPath`: the `workflow.js` file next to this SKILL.md (absolute path)
- `args`: `{ "question": "<restated question at the category level>", "objective": "<what the user wants to achieve, or empty>", "context": "<constraints, what they tried, defaults you chose>", "examples": ["<illustrative example>: <the traits that make it relevant>"], "today": "<YYYY-MM-DD>", "depth": "standard" | "max", "min_words": <optional override of the body-length floor> }`. Leave `examples` empty when the example *is* the subject.

What it does:

1. **Plan**: three scouts (primary-source view, community view, contrarian view) map the landscape and insider vocabulary; a planner decomposes the question into 8–14 sub-questions, each with concrete search angles, including forum/community angles and one lateral angle.
2. **Research**: every sub-question gets three researchers in parallel with disjoint mandates (primary/official, community/forums, contrarian/counter-evidence). Each must run 10–15+ searches and read 8–12+ full sources; thin results trigger a second pass. Community researchers get explicit forum-mining rules and platform recipes (Reddit JSON/old.reddit/pullpush, HN Algolia, Stack Exchange API, GitHub, Discourse JSON, YouTube transcripts, Wayback). Every claim carries a URL and a verbatim quote. Researchers report structured **leads** (threads, tools, people, documents, terms, events) they met but did not exhaust.
3. **Swarm**: a triage agent scores every lead (with a script-computed floor so hot leads cannot be parked) and picks which deserve a **swarm**: 5–6 agents (standard) or 8–12 (max), each with a distinct angle chosen by entity type. A thread swarm, for example, reads the whole thread sorted by top, then by new/controversial, follows every link, finds the primary sources behind the repeated claims, sweeps every other community for the same topic, hunts rebuttals, profiles commenter credibility, and extracts every number. A dossier compiler merges the swarm into one entity dossier. Leads found by swarms feed the next round (depth up to 2, or 3 in max), so one discovery leads to the next. Lesser leads get a single follow-up agent; the rest are parked and listed in the appendix.
4. **Verify**: every claim is quote-checked against its page by a citation checker (with archive fallbacks); failures go to a re-sourcer, and claims that still fail are excluded from the body. Key and community claims then go through 3-skeptic panels that try to refute them with independent sources; split votes go to an adjudicator. Statuses: confirmed, source_checked, contested, refuted, outdated, citation_failed.
5. **Direct**: a research director and an independent stop auditor (whose job is to argue the research is *not* done) each see the full ledger and dossiers, rate coverage on six dimensions, and propose new sub-questions. The loop continues until both say done with nothing thin (min 2 rounds, max 4; 3/6 in max).
6. **Write**: an outline agent assigns every claim to sections following a fixed skeleton (scope, landscape, theme sections, one deep-dive section per dossier, quantitative picture, disagreements, debunked claims, what practitioners say, recommendations if there is an objective, discovery trail, unknowns, confidence). One writer per section runs in parallel with a word minimum (body floor 9,000 words, 16,000 in max); short sections are re-run with the unused claims attached. A stitcher writes the executive summary, reading guide, bridges and glossary. The script generates appendices: full claim table, annotated source list, community voices, timeline, numbers, glossary, entity dossiers, dissent register, unexplored leads, methodology and review log.
7. **Review**: up to 3 passes (5 in max). Each pass runs citation auditors (every cited source re-opened and checked against the sentences that cite it) plus lenses for completeness-vs-ledger, anchoring/bias, logic, structure, domain-expert objections, numbers, recency, community-voice fidelity and (with an objective) recommendations. A managing-editor agent merges and triages the issues; issues needing new evidence trigger gap research and verification; affected sections are rewritten in parallel with a no-shrink rule. The loop exits when no critical/major issues remain.

The return value includes the assembled report (markdown with resolved numbered citations), word counts, swarm list, claim statistics, review log, agents used and any budget downgrades. If the run is interrupted, resume with `resumeFromRunId`; completed agents are reused from cache.

## 3. Deliver

- Spot-check: open 3–5 of the most load-bearing citations yourself (and anything the last review pass still flagged) and confirm they say what the report claims. Fix anything wrong by editing the markdown.
- Publish the full report as an Artifact (load `artifact-design` first). It is long: keep the table of contents, give every section an anchor, render the appendices' tables as tables, and make sure it reads well on a phone.
- In chat give a short summary: the bottom line, overall confidence, words in the body, claims confirmed / source-checked / contested / refuted out of the total, swarms run (entity names), review passes and blocking issues remaining, and anything the workflow reports as unresearched or parked. Don't hide weaknesses.

## Without the Workflow tool

If Workflow isn't available, run the same phases by hand with the Agent tool: scouts, then researcher trios in one parallel message, then a triage pass and swarm agents for the top leads, then quote-checkers and skeptics, then the director, then section writers, then reviewers. Use the prompt blocks in `workflow.js` verbatim.
