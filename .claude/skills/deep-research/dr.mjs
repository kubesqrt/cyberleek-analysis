#!/usr/bin/env node
// Orchestrator-mode deep research. The Workflow tool caps concurrency at (CPUs - 2) per workflow, which on small
// containers means 2 agents at a time. This CLI keeps the same design as workflow.js but lets the main Claude session
// drive the fan-out with the Agent tool: each command writes prompt files for one phase, the session launches one
// agent per prompt (all in parallel), each agent writes its JSON result to out/, and the next command absorbs them.
//
//   DR_RUN=<run dir> node dr.mjs <command> [args]
//
// Phase order (R = round):
//   init <args.json>            → prompts/scout-*.md
//   plan                        → prompts/plan.md
//   absorb-plan
//   research                    → prompts/research-r{R}-{sq}-{mandate}.md
//   absorb-research             → writes second-pass prompts for thin sub-questions (run them, then absorb-research --final)
//   triage                      → prompts/triage-r{R}.md (or NONE)
//   absorb-triage               → prompts/swarm-*.md, prompts/followup-*.md
//   absorb-swarms               → prompts/dossier-*.md
//   absorb-dossiers
//   quotecheck / absorb-quotecheck (→ prompts/resource-*.md) / absorb-resource
//   skeptics / absorb-skeptics (→ prompts/adjudicate-*.md) / absorb-adjudicate
//   direct / absorb-direct      → prints CONTINUE or STOP
//   outline / absorb-outline    → prompts/write-*.md
//   absorb-sections             → prompts/expand-*.md for short sections; then absorb-sections --final
//   stitch / absorb-stitch
//   review <pass> / absorb-reviews <pass> → prompts/rtriage-{pass}.md
//   absorb-rtriage <pass>       → prompts/gap-*.md (then quotecheck/skeptics cycle) and prompts/rewrite-*.md
//   absorb-rewrites <pass>      → prints PUBLISHABLE or ANOTHER_PASS
//   assemble                    → report.md
//   status
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, unlinkSync } from 'node:fs'
import { join } from 'node:path'

const RUN = process.env.DR_RUN
if (!RUN) { console.error('set DR_RUN=<run dir>'); process.exit(1) }
const P = join(RUN, 'prompts'), O = join(RUN, 'out'), STATE = join(RUN, 'state.json')
for (const d of [RUN, P, O]) if (!existsSync(d)) mkdirSync(d, { recursive: true })
const [cmd, ...rest] = process.argv.slice(2)
const flag = f => rest.includes(f)
const arg0 = rest.find(a => !a.startsWith('--'))

const load = () => JSON.parse(readFileSync(STATE, 'utf8'))
const save = s => writeFileSync(STATE, JSON.stringify(s))
const readOut = name => { const f = join(O, name + '.json'); if (!existsSync(f)) return null; try { return JSON.parse(readFileSync(f, 'utf8')) } catch (e) { console.log(`INVALID_JSON out/${name}.json`); return null } }
const wc = s => (s || '').trim().split(/\s+/).filter(Boolean).length
const chunk = (arr, n) => { const out = []; for (let i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n)); return out }
const normUrl = u => (u || '').toLowerCase().replace(/^https?:\/\/(www\.|old\.|new\.|m\.)?/, '').replace(/[?#].*$/, '').replace(/\/+$/, '')
const host = u => { const m = (u || '').match(/^https?:\/\/([^/]+)/i); return m ? m[1].toLowerCase().replace(/^www\./, '') : '' }
const esc = s => String(s || '').replace(/\|/g, '\\|').replace(/\n+/g, ' ')
const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40)

// ---------------------------------------------------------------- prompt emission
let emitted = []
function emit(name, body, schema, outName = name) {
  const outPath = join(O, outName + '.json')
  const contract = `# Agent task

OUTPUT CONTRACT (mandatory): when you finish, write your result as ONE JSON object to the file \`${outPath}\` using the Write tool. The object must have this shape (JSON Schema):
\`\`\`json
${JSON.stringify(schema)}
\`\`\`
Every "required" key must be present. Strings must be plain text (no markdown fences around the JSON). If you genuinely found nothing for an array field, write an empty array, never omit it. Do not write anything else to disk. Your final chat message must be exactly one line: \`DONE ${outPath}\` followed by a short note of what you covered and anything that blocked you.

---

`
  writeFileSync(join(P, name + '.md'), contract + body)
  emitted.push({ prompt: join(P, name + '.md'), out: outPath })
}
function flushEmitted(label) {
  if (!emitted.length) { console.log(`NONE ${label}`); return }
  console.log(`PROMPTS ${label} ${emitted.length}`)
  for (const e of emitted) console.log(e.prompt)
  emitted = []
}
const expectOuts = (names) => { const missing = names.filter(n => !existsSync(join(O, n + '.json'))); if (missing.length) console.log(`MISSING ${missing.length}: ${missing.join(' ')}`); return missing }

// ---------------------------------------------------------------- schemas (same as workflow.js)
const SUBQ_ITEM = { type: 'object', properties: { id: { type: 'string' }, question: { type: 'string' }, why: { type: 'string' }, search_angles: { type: 'array', items: { type: 'string' } } }, required: ['id', 'question', 'search_angles'] }
const PLAN = { type: 'object', properties: { restated_question: { type: 'string' }, field: { type: 'string' }, assumptions: { type: 'array', items: { type: 'string' } }, subquestions: { type: 'array', items: SUBQ_ITEM } }, required: ['restated_question', 'field', 'subquestions'] }
const ORIENT = { type: 'object', properties: { landscape: { type: 'string', description: '300-600 words' }, insider_terms: { type: 'array', items: { type: 'string' } }, key_entities: { type: 'array', items: { type: 'string' } }, where_the_data_lives: { type: 'array', items: { type: 'string' } }, communities: { type: 'array', items: { type: 'string' } } }, required: ['landscape', 'insider_terms', 'key_entities', 'communities'] }
const CLAIM = { type: 'object', properties: { claim: { type: 'string' }, url: { type: 'string' }, title: { type: 'string' }, quote: { type: 'string', description: 'verbatim, <= 60 words' }, source_type: { type: 'string', enum: ['primary', 'secondary', 'community', 'weak'] }, published: { type: 'string' }, author: { type: 'string' }, key: { type: 'boolean' }, confidence: { type: 'string', enum: ['high', 'medium', 'low'] }, access_note: { type: 'string' } }, required: ['claim', 'url', 'title', 'quote', 'source_type', 'key', 'confidence'] }
const LEAD = { type: 'object', properties: { lead: { type: 'string' }, entity_type: { type: 'string', enum: ['thread', 'community', 'tool', 'person', 'org', 'term', 'document', 'event', 'dataset', 'business_idea', 'other'] }, name: { type: 'string' }, canonical_url: { type: 'string' }, found_in: { type: 'array', items: { type: 'string' } }, mention_count: { type: 'integer' }, size_hint: { type: 'string' }, relevance: { type: 'string', enum: ['central', 'supporting', 'tangential'] }, contested: { type: 'boolean' }, hops_taken: { type: 'integer' }, what_is_unknown: { type: 'string' } }, required: ['lead', 'entity_type', 'name', 'relevance', 'mention_count', 'hops_taken', 'what_is_unknown'] }
const VOICE = { type: 'object', properties: { quote: { type: 'string', description: 'verbatim, <= 80 words' }, author: { type: 'string' }, platform: { type: 'string' }, url: { type: 'string' }, date: { type: 'string' }, stance: { type: 'string', enum: ['supports_consensus', 'dissents', 'nuance', 'firsthand_experience', 'expert'] }, credibility: { type: 'string' }, upvotes: { type: 'string' } }, required: ['quote', 'author', 'platform', 'url', 'stance', 'credibility'] }
const NUMBER = { type: 'object', properties: { what: { type: 'string' }, value: { type: 'string' }, who: { type: 'string' }, url: { type: 'string' }, date: { type: 'string' }, challenged: { type: 'boolean' } }, required: ['what', 'value', 'url'] }
const TIMELINE = { type: 'object', properties: { date: { type: 'string' }, event: { type: 'string' }, url: { type: 'string' } }, required: ['date', 'event'] }
const FINDINGS = { type: 'object', properties: { summary: { type: 'string', description: '200-500 words' }, claims: { type: 'array', items: CLAIM }, voices: { type: 'array', items: VOICE }, numbers: { type: 'array', items: NUMBER }, timeline: { type: 'array', items: TIMELINE }, contradictions: { type: 'array', items: { type: 'string' } }, unanswered: { type: 'array', items: { type: 'string' } }, leads: { type: 'array', items: LEAD }, sources_read: { type: 'array', items: { type: 'string' } }, searches_run: { type: 'array', items: { type: 'string' } }, coverage_note: { type: 'string' } }, required: ['summary', 'claims', 'voices', 'numbers', 'contradictions', 'unanswered', 'leads', 'sources_read', 'searches_run'] }
const SWARM_FINDINGS = { ...FINDINGS, properties: { ...FINDINGS.properties, angle: { type: 'string' }, recurring_claims: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, supporters: { type: 'integer' }, dissenters: { type: 'integer' }, strongest_evidence_url: { type: 'string' }, strongest_dissent_quote: { type: 'string' } }, required: ['claim', 'supporters', 'dissenters'] } }, answers: { type: 'array', items: { type: 'object', properties: { question: { type: 'string' }, answer: { type: 'string' } }, required: ['question', 'answer'] } } }, required: [...FINDINGS.required, 'angle', 'recurring_claims', 'answers', 'coverage_note'] }
const DOSSIER = { type: 'object', properties: { name: { type: 'string' }, entity_type: { type: 'string' }, one_paragraph: { type: 'string' }, what_it_is: { type: 'string', description: '400-1000 words' }, consensus_claims: { type: 'array', items: { type: 'string' } }, dissent: { type: 'array', items: { type: 'string' } }, primary_sources: { type: 'array', items: { type: 'string' } }, credibility_assessment: { type: 'string' }, relation_to_question: { type: 'string' }, open_questions: { type: 'array', items: { type: 'string' } }, recommended_followups: { type: 'array', items: LEAD } }, required: ['name', 'entity_type', 'one_paragraph', 'what_it_is', 'consensus_claims', 'dissent', 'credibility_assessment', 'relation_to_question', 'open_questions', 'recommended_followups'] }
const TRIAGE = { type: 'object', properties: { decisions: { type: 'array', items: { type: 'object', properties: { key: { type: 'string' }, tier: { type: 'string', enum: ['swarm', 'followup', 'park'] }, why: { type: 'string' }, questions_to_answer: { type: 'array', items: { type: 'string' } } }, required: ['key', 'tier', 'why', 'questions_to_answer'] } } }, required: ['decisions'] }
const QUOTE_CHECKS = { type: 'object', properties: { checks: { type: 'array', items: { type: 'object', properties: { claim_id: { type: 'string' }, reachable: { type: 'boolean' }, archive_url_used: { type: 'string' }, quote_found: { type: 'string', enum: ['verbatim', 'near_verbatim', 'paraphrase_only', 'not_found'] }, supports_claim: { type: 'string', enum: ['yes', 'partially', 'no', 'out_of_context'] }, page_date: { type: 'string' }, note: { type: 'string' } }, required: ['claim_id', 'reachable', 'quote_found', 'supports_claim'] } } }, required: ['checks'] }
const VERDICTS = { type: 'object', properties: { verdicts: { type: 'array', items: { type: 'object', properties: { claim_id: { type: 'string' }, status: { type: 'string', enum: ['confirmed', 'refuted', 'unclear', 'outdated'] }, evidence_url: { type: 'string' }, note: { type: 'string' } }, required: ['claim_id', 'status', 'note'] } } }, required: ['verdicts'] }
const COVER = { type: 'string', enum: ['thin', 'adequate', 'strong'] }
const GAPS = { type: 'object', properties: { done: { type: 'boolean' }, coverage_assessment: { type: 'object', properties: { breadth: COVER, depth: COVER, counter_evidence: COVER, recency: COVER, quantitative: COVER, community: COVER }, required: ['breadth', 'depth', 'counter_evidence', 'recency', 'quantitative', 'community'] }, reasoning: { type: 'string' }, new_subquestions: { type: 'array', items: SUBQ_ITEM } }, required: ['done', 'coverage_assessment', 'reasoning', 'new_subquestions'] }
const OUTLINE = { type: 'object', properties: { title: { type: 'string' }, sections: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, title: { type: 'string' }, purpose: { type: 'string' }, claim_ids: { type: 'array', items: { type: 'string' } }, dossier_names: { type: 'array', items: { type: 'string' } }, voice_filter: { type: 'string' }, min_words: { type: 'integer' }, target_words: { type: 'integer' }, must_cover: { type: 'array', items: { type: 'string' } }, tables: { type: 'array', items: { type: 'string' } } }, required: ['id', 'title', 'purpose', 'claim_ids', 'min_words', 'target_words', 'must_cover'] } } }, required: ['title', 'sections'] }
const SECTION = { type: 'object', properties: { id: { type: 'string' }, title: { type: 'string' }, markdown: { type: 'string', description: 'full section markdown citing only [S#] and [C####] tokens; no H2 heading' }, word_count: { type: 'integer' }, claim_ids_used: { type: 'array', items: { type: 'string' } }, length_reduction_justified: { type: 'boolean' } }, required: ['id', 'title', 'markdown', 'word_count', 'claim_ids_used'] }
const FRONT = { type: 'object', properties: { executive_summary: { type: 'string', description: '600-1000 words' }, how_to_read: { type: 'string', description: '300+ words' }, bridges: { type: 'array', items: { type: 'object', properties: { section_id: { type: 'string' }, text: { type: 'string' } }, required: ['section_id', 'text'] } }, glossary: { type: 'string' } }, required: ['executive_summary', 'how_to_read', 'bridges', 'glossary'] }
const ISSUE = { type: 'object', properties: { id: { type: 'string' }, severity: { type: 'string', enum: ['critical', 'major', 'minor', 'nit'] }, section_id: { type: 'string' }, offending_text: { type: 'string' }, problem: { type: 'string' }, proposed_fix: { type: 'string' }, evidence_ids: { type: 'array', items: { type: 'string' } }, needs_research: { type: 'boolean' }, research_question: { type: 'string' }, touches_conclusions: { type: 'boolean' } }, required: ['id', 'severity', 'section_id', 'offending_text', 'problem', 'proposed_fix', 'needs_research', 'touches_conclusions'] }
const REVIEW = { type: 'object', properties: { lens: { type: 'string' }, overall: { type: 'string' }, issues: { type: 'array', items: ISSUE } }, required: ['lens', 'overall', 'issues'] }
const REVIEW_TRIAGE = { type: 'object', properties: { accepted: { type: 'array', items: ISSUE }, rejected: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, why: { type: 'string' } }, required: ['id', 'why'] } }, pass_verdict: { type: 'string', enum: ['publishable', 'needs_another_pass'] } }, required: ['accepted', 'rejected', 'pass_verdict'] }

// ---------------------------------------------------------------- prompt blocks
function blocks(S) {
  const Q = S.args, MAX = S.MAX
  const OBJECTIVE_NOTE = Q.objective ? `USER'S OBJECTIVE (what they want to achieve with this research): ${Q.objective}\nFavour findings that are actionable for this objective: options, approaches, tools, pitfalls and tips that real people report.` : ''
  const EXAMPLES = Q.examples || []
  const EXAMPLES_NOTE = EXAMPLES.length ? `ILLUSTRATIVE EXAMPLES (given by the user to show what they mean; they are NOT the research target):\n${EXAMPLES.map(e => `- ${e}`).join('\n')}\nResearch the general category these examples belong to. An example may appear as one data point among many, never as the focus.` : ''
  const TOOLS_NOTE = `Tools: first run ToolSearch with query "select:WebSearch,WebFetch" to load web tools.
Use WebSearch mode "extended" for anything niche, recent, numeric or contested; "standard" for quick lookups.
Open and read the actual pages with WebFetch. Never cite a page from its search snippet or from another site's summary of it.
Today's date: ${Q.today}.`
  const SOURCE_RULES = `Source rules:
- Prefer primary sources: official docs, filings, datasets, papers, statutes, standards, the original announcement, the author's own words.
- SEO blogs, content farms, AI-generated summaries and undated pages are "weak"; use them only to find primary sources.
- Forum/community posts are source_type "community": experience reports and leads, not established fact. They are strong only when several independent users report the same thing.
- Record the publication date and title of every source. Flag anything that may be outdated.
- Every claim needs a URL plus a short verbatim quote that supports it. No quote, no claim.
- Separate fact from opinion/forecast. Note when sources disagree instead of picking one silently.
- If you cannot find something, say so. Never fill gaps from memory.`
  const LEAD_RULES = `Leads: every tool, person, organisation, document/study, thread, community, term, event or candidate business idea you meet that deserves its own investigation goes in leads[], with entity_type, name, canonical_url, how many distinct sources mentioned it, and the specific questions you could not answer about it. Mark relevance "central" if it could change the answer or a recommendation. Follow each lead one hop so you can describe it, then hand it over: dedicated swarms do the deep chasing.`
  const FORUM_RULES = `Forum mining rules (exhaustive coverage, not sampling):
1. Determine the thread's size (comments, pages) before reading. Read EVERY page. Record "page X of Y" in coverage_note. If you stop early, say exactly where and why.
2. Read once sorted by top/best (what the community endorses), then by new (late corrections, OP updates), then by controversial (the dissent).
3. Expand collapsed content: "load more comments", "continue this thread", "N more replies". Fetch each stub's permalink.
4. Read reply chains, not just top-level comments. A top comment is often corrected three replies down. Record who won each argument by evidence, not votes.
5. Follow every link in the thread. For each: what the linker claimed it says vs what it actually says.
6. Extract recurring claims with counts of DISTINCT users asserting and disputing each (400 upvotes on one comment is one anecdote).
7. Catalogue dissenters separately with their strongest quote and credibility signals.
8. Credibility signals: account age, karma/reputation/trust level, flair or verified role, maintainer/employee badge, domain post history, self-disclosed affiliation, whether others defer to them, whether they were later corrected.
9. Date everything and note whether anything since (new version, policy change, newer thread) may have changed it.
10. Preserve voice: keep 10-30 verbatim quotes (<= 80 words) carrying firsthand experience, expert nuance or sharp dissent, with username, date, link, votes.
11. Search the same community for the topic across years with at least 5 phrasings including insider vocabulary, sorted by top (all time) and by new; page through all results.`
  const PLATFORM_RECIPES = `Platform recipes (use these when a page is blocked, paginated or hides content):
REDDIT: thread JSON https://old.reddit.com/r/<sub>/comments/<id>/<slug>/.json?limit=500&sort=top&raw_json=1 (vary sort=new|controversial|old; add &depth=10). "more" stubs: fetch the comment permalink .../<commentid>/.json?context=0&limit=500. HTML fallbacks: old.reddit.com?limit=500, redlib mirrors (instance list: github.com/redlib-org/redlib-instances), https://r.jina.ai/<url>. Subreddit search: https://old.reddit.com/r/<sub>/search.json?q=<q>&restrict_sr=on&sort=top&t=all&limit=100 (paginate &after=), plus web search site:reddit.com/r/<sub> <q>. Historical/removed content: https://api.pullpush.io/reddit/search/comment/?q=<q>&subreddit=<sub>&size=100 and /submission/, arctic-shift.photon-reddit.com, Wayback https://web.archive.org/web/2/<url>, archive.ph. Users: https://old.reddit.com/user/<name>/about.json, /comments.json?sort=top&limit=100.
HACKER NEWS: search https://hn.algolia.com/api/v1/search?query=<q>&tags=story&hitsPerPage=100 (tags=comment for comments; search_by_date for recency; numericFilters=points>20). Full thread, every comment, one call: https://hn.algolia.com/api/v1/items/<id>. Users: https://hn.algolia.com/api/v1/users/<name>. Domain: https://news.ycombinator.com/from?site=<domain>.
STACK EXCHANGE: https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=votes&q=<q>&site=<site>&filter=withbody&pagesize=100; answers /2.3/questions/<id>/answers?order=desc&sort=votes&site=<site>&filter=withbody; comments /2.3/answers/<id>/comments?site=<site>&filter=withbody. Distinguish accepted vs highest-voted vs most recent.
GITHUB: issues sorted by reactions https://github.com/<o>/<r>/issues?q=<q>+is%3Aissue+sort%3Areactions-%2B1-desc (also is:closed, wontfix labels); REST https://api.github.com/repos/<o>/<r>/issues/<n>/comments?per_page=100; discussions ?discussions_q=; releases/CHANGELOG for dating; author_association marks maintainers.
DISCOURSE forums: https://<forum>/t/<slug>/<id>.json gives posts_count and all post ids in post_stream.stream; fetch the rest via /t/<id>/posts.json?post_ids[]=<id>&post_ids[]=<id> (20 per call) or ?print=true. Search /search.json?q=<q> order:latest (modifiers in:title, after:, category:, status:solved, order:likes). Users /u/<name>.json.
YOUTUBE: watch page meta for date/channel; transcripts and comments via Invidious instances (https://api.invidious.io/instances.json; /api/v1/captions/<id>, /api/v1/comments/<id>?sort_by=top) or Piped (pipedapi.kavin.rocks/streams/<id>, /comments/<id>). Try at least two mirrors; never claim a video said something without a transcript quote.
OTHER: phpBB viewtopic.php?t=<id>&start=<n>; XenForo /threads/<slug>.<id>/page-N; Lemmy /api/v3/comment/list?post_id=<id>&max_depth=8; Discord archives via linen.dev and answeroverflow.com; Telegram https://t.me/s/<channel>?q=<term>; X/Twitter is unreliable (nitter/Wayback, else say unverifiable). Review sites: read 1-star and 5-star sorted by recent; watch for review bursts. Paywalled: Wayback, archive.ph, r.jina.ai, AMP, arXiv/SSRN/author pages. Acquisition marketplaces (Acquire.com, Flippa, Empire Flippers, Motion Invest) list revenue and multiples; Indie Hackers product pages and Starter Story interviews report founder revenue; Product Hunt shows launch traction.
Record which mirror or fallback you used in coverage_note or access_note.`
  const STATUS_LEGEND = `Status labels: confirmed = quote verified on the page AND independent fact-checkers found independent support; source_checked = quote verified on the cited page but not independently corroborated (non-key claims); contested = checkers split or evidence conflicts; refuted = independent evidence contradicts it; outdated = was true, no longer is. Source types: primary, secondary, community (forum/user reports), weak.`
  return { OBJECTIVE_NOTE, EXAMPLES, EXAMPLES_NOTE, TOOLS_NOTE, SOURCE_RULES, LEAD_RULES, FORUM_RULES, PLATFORM_RECIPES, STATUS_LEGEND }
}

// ---------------------------------------------------------------- ledger helpers
function addSource(S, c) {
  const k = normUrl(c.url); if (!k) return null
  if (!S.sources[k]) { S.sourceCounter++; S.sources[k] = { id: `S${S.sourceCounter}`, n: S.sourceCounter, url: c.url, title: c.title || c.url, platform: host(c.url), source_type: c.source_type, published: c.published || '', claim_ids: [] } }
  return S.sources[k]
}
function absorb(S, found, origin) {
  if (!found || !Array.isArray(found.claims)) return null
  const ids = []
  for (const c of found.claims) {
    if (!c || !c.url || !c.quote || !c.claim) continue
    const s = addSource(S, c); if (!s) continue
    S.claimCounter++
    const id = `C${String(S.claimCounter).padStart(4, '0')}`
    S.claims.push({ ...c, id, sid: s.id, origin, status: 'pending', notes: [] }); s.claim_ids.push(id); ids.push(id)
  }
  for (const v of found.voices || []) if (v && v.quote) S.voices.push({ ...v, origin: origin.ref, entity: origin.entity || '' })
  for (const n of found.numbers || []) if (n && n.what) S.numbers.push({ ...n, origin: origin.ref })
  for (const t of found.timeline || []) if (t && t.event) S.timeline.push({ ...t, origin: origin.ref })
  const e = { id: origin.ref, question: origin.question, kind: origin.kind, round: origin.round, depth: origin.depth || 0, entity: origin.entity || '', summary: found.summary || '', claim_ids: ids, unanswered: found.unanswered || [], contradictions: found.contradictions || [], coverage: found.coverage_note || '', leads: (found.leads || []).filter(l => l && l.name), recurring: found.recurring_claims || [], answers: found.answers || [] }
  S.entries.push(e)
  return e
}
const claimById = (S, id) => S.claims.find(c => c.id === id)
const claimLine = c => `${c.id} [${c.status}] [${c.source_type}${c.published ? ', ' + c.published : ''}] ${c.claim} — ${c.sid}`
const claimFull = c => `${c.id} [${c.status}] [${c.source_type}${c.published ? ', ' + c.published : ''}] ${c.claim}\n    source ${c.sid}: ${c.title} — ${c.url}${c.access_note ? ` (${c.access_note})` : ''}\n    quote: "${c.quote}"${c.notes.length ? `\n    verification: ${c.notes.join(' | ')}` : ''}`
const stats = S => { const s = {}; for (const c of S.claims) s[c.status] = (s[c.status] || 0) + 1; return s }
const statLine = S => Object.entries(stats(S)).map(([k, v]) => `${k} ${v}`).join(', ')
const entityKey = l => ((l.canonical_url ? normUrl(l.canonical_url) : '') + '|' + (l.name || '')).toLowerCase().replace(/[^a-z0-9|]+/g, '')
const sourceList = S => Object.values(S.sources).sort((a, b) => a.n - b.n)
const usable = S => S.claims.filter(c => c.status !== 'citation_failed')

function mergeFindings(list) {
  const f = list.filter(Boolean); if (!f.length) return null
  const cat = k => f.flatMap(x => Array.isArray(x[k]) ? x[k] : [])
  return { summary: f.map(x => x.summary || '').join('\n\n'), claims: cat('claims'), voices: cat('voices'), numbers: cat('numbers'), timeline: cat('timeline'), contradictions: cat('contradictions'), unanswered: cat('unanswered'), leads: cat('leads'), sources_read: cat('sources_read'), searches_run: cat('searches_run'), coverage_note: f.map(x => x.coverage_note || '').filter(Boolean).join(' / ') }
}

// ---------------------------------------------------------------- swarm angles
const ANGLES = {
  thread: [['top', 'Read the WHOLE thread sorted by top/best, every page, expanding every collapsed chain.'], ['new-controversial', 'Read the WHOLE thread sorted by new and then by controversial: late corrections, OP updates, the dissent the top sort buries.'], ['links', 'Collect every outbound link in the thread (OP and comments), open each, record what it actually says vs how the commenter characterised it.'], ['primary-sources', 'For the 5-10 most repeated factual claims in the thread, find the original source (docs, paper, filing, commit, announcement) and quote it.'], ['cross-community', "Search this thread's topic and insider vocabulary across every other community (other subreddits, HN, SE, Discourse forums, GitHub, YouTube, blogs); report agreement and disagreement with this thread's consensus. Open at least 15 other threads."], ['contrarian', 'Hunt rebuttals: "this is wrong because", later threads revisiting the topic, people who tried it and failed, experts who disagree.'], ['credibility', 'Profile the 8-12 most influential commenters: account age, karma/trust, flair, domain post history, self-disclosed affiliation, whether their claims were later corrected.'], ['timeline', 'When was the thread; what changed since (versions, policies, newer threads); is the consensus still current as of today?'], ['siblings', "Find the same community's other threads on this topic across years (5+ phrasings, sorted top and new, paginate) and show how the consensus moved."], ['quant', 'Extract every number, price, benchmark, date and version in the thread into numbers[], with who said it and whether it was challenged.']],
  community: [['canon', 'Wiki, sidebar, FAQ, pinned posts and rules of the community: what it treats as settled.'], ['top-alltime', 'Top posts of all time on the topic (5+ search phrasings, sorted top, paginate all results).'], ['top-recent', 'Top posts of the last 12 months on the topic; what is new or changing.'], ['new', 'Newest posts on the topic sorted by new: unresolved questions, fresh complaints.'], ['recurring', 'Extract the recurring claims with distinct-user support/dissent counts across the threads you read.'], ['dissent', 'Catalogue the dissenters and minority views, with their strongest quotes and credibility.'], ['power-users', 'Profile moderators and the most-cited power users: expertise, affiliations, incentives.'], ['siblings', 'Sibling communities on the same topic and how they differ from this one.'], ['timeline', "Timeline of how the community's consensus shifted over the years."], ['quant', 'Every number, price, benchmark, date anyone states, with who and whether challenged.']],
  tool: [['official', 'Official docs, changelog/releases, pricing, licensing, stated limitations.'], ['issues', 'GitHub (or tracker) issues and discussions: top-reacted open bugs, closed-wontfix, maintainer responses, release cadence, bus factor.'], ['sentiment', 'Community sentiment sweep across Reddit/HN/forums, top and new, across years, with voices.'], ['comparisons', 'Head-to-head comparisons against named alternatives, with the criteria people use.'], ['failures', 'Failure and horror stories, migrations away, "we switched from X because".'], ['maker', 'Maker/company background: funding, business model, ownership changes, incentives, trust signals.'], ['adoption', 'Adoption/traction evidence: downloads, stars trajectory, job posts, case studies, who uses it.'], ['security-legal', 'Security, compliance and legal incidents or concerns.'], ['expert-reviews', 'Expert/longform reviews and benchmarks.'], ['credibility', 'Profile the loudest advocates and critics: affiliations, incentives, track record.'], ['quant', 'Every number (prices, benchmarks, limits, versions, dates) into numbers[], with source and whether challenged.']],
  business_idea: [['customers', 'Who exactly the customers are: segments, job titles or situations, where they gather online (specific subreddits, forums, Slack/Discord groups, marketplaces), how many there are, what they currently pay for and complain about. Quote them.'], ['incumbents', 'The existing players proving demand: pricing pages, plans, estimated revenue (Indie Hackers, Starter Story, acquisition listings, press), customer counts, what reviewers and forum users say they do badly. At least 5 players.'], ['founder-reports', 'Real founder reports of launching this kind of business: revenue over time, time to first paying customer, what channel actually worked, what they would do differently. Indie Hackers, Reddit r/SaaS r/microsaas r/Entrepreneur r/juststart, HN, Starter Story, MicroConf, Twitter/X threads via mirrors, YouTube transcripts.'], ['channel-proof', 'Proof that a faceless acquisition channel works for this idea: SEO (keyword volumes, difficulty, example ranking sites and their traffic), paid ads (CPC/CPA reports), marketplaces/app stores, partnerships, cold outreach, anonymous social/brand accounts. Numbers with sources.'], ['economics', 'Unit economics: typical price points, conversion rates, churn, CAC, gross margin, tooling and contractor costs, what $25k-$50k buys. Every number with who said it.'], ['failures', 'Post-mortems and failure modes: why businesses like this die (platform dependency, API/policy changes, AI commoditisation, competition, churn, legal). Base rates where anyone has measured them.'], ['why-now', 'What changed in 2024-2026 that makes this more or less viable: AI tooling, platform policies, ad costs, Google AI Overviews, payment/tax rules, new APIs or data sources. Dated evidence.'], ['faceless-fit', 'Evidence on whether this can be run without a founder face: examples of faceless/brand-only operators in this niche, what they do for trust (reviews, guarantees, brand content), and where a personal brand is actually required.'], ['variants', 'Adjacent variants and sub-niches of the idea: narrower verticals, different buyer, different pricing model, B2B vs B2C; which variant has the best evidence.'], ['speed-to-revenue', 'How fast comparable solo founders got to first dollar and to $5k/month, and what the 2-3 month build+launch plan looks like for a technical solo founder using AI tooling; realistic weekly hour needs.'], ['legal-ops', 'Legal, compliance, payments, tax, platform ToS and operational constraints for this idea (data licensing, scraping, financial regulation, app-store rules, chargebacks).'], ['quant', 'Every number stated anywhere about this idea (prices, revenue, traffic, CPCs, churn, market size) into numbers[], with who said it and whether challenged.']],
  person: [['own-words', 'Their own writings, talks, repos, posts in full.'], ['interviews', 'Interviews and podcasts (transcripts).'], ['reception', 'What others say about them: praise and criticism, with voices.'], ['incentives', 'Conflicts of interest, affiliations, business incentives.'], ['track-record', 'Past claims/predictions and how they aged.'], ['network', 'Network and affiliations; who amplifies them and why.'], ['timeline', 'Timeline of their involvement with this topic.'], ['cross-community', 'Mentions across communities and how different communities view them.'], ['primary-sources', 'Primary sources behind their headline claims.']],
  term: [['origin', 'Origin and canonical definition: first use, defining paper/doc.'], ['variants', 'Variants and competing definitions; where they conflict.'], ['literature', 'Academic/technical literature using the term.'], ['practice', 'How practitioners actually use it in forums; what it implies for them.'], ['critiques', 'Critiques: "this term is misleading", misuse, hype.'], ['measurement', 'How it is measured or quantified, with numbers.'], ['adjacent', 'Equivalents in adjacent fields.'], ['timeline', "Timeline of the term's adoption and shifts in meaning."]],
  document: [['full-read', 'Read the full document: all sections, tables, appendices, supplementary material.'], ['methods', 'Methodology and limitations as stated by the authors, and as critics see them.'], ['citers', 'Who cites it and for what; do they characterise it correctly?'], ['replication', 'Replications, critiques, retractions, errata.'], ['followups', "The authors' follow-ups and later work."], ['coverage', 'Press and forum coverage vs what the document actually says.'], ['data', 'Data/code availability and what the data shows.'], ['competitors', 'Competing documents/studies on the same question.'], ['credibility', 'Authors, funders and their incentives.']],
  event: [['primary', 'Timeline from primary statements and official records.'], ['reporting', 'Independent reporting.'], ['eyewitness', 'Forum eyewitness/participant accounts, with voices.'], ['response', 'Official responses and post-mortems.'], ['aftermath', 'Aftermath and consequences.'], ['disputed', 'Disputed facts and competing narratives.'], ['precedents', 'Similar prior incidents.'], ['quant', 'Every number and date, with source and whether challenged.']],
}
ANGLES.org = ANGLES.person; ANGLES.dataset = ANGLES.document; ANGLES.other = ANGLES.tool
const anglesFor = (S, type) => { const a = ANGLES[type] || ANGLES.other; return S.MAX ? a.slice(0, 12) : a.slice(0, Math.min(6, a.length)) }

// ---------------------------------------------------------------- commands
const K = S => ({ MIN_ROUNDS: S.MAX ? 3 : 2, MAX_ROUNDS: S.MAX ? 6 : 4, SKEPTICS: 3, CHUNK: 12, JUDGE_CHUNK: 10, SWARMS_PER_ROUND: S.MAX ? 12 : 6, MAX_SWARMS: S.MAX ? 40 : 18, MAX_DEPTH: S.MAX ? 3 : 2, MIN_SOURCES: S.MAX ? 12 : 8, MIN_SEARCHES: S.MAX ? 15 : 10, MIN_BODY_WORDS: S.args.min_words || (S.MAX ? 16000 : 9000), MAX_REVIEW_PASSES: S.MAX ? 5 : 3 })

const commands = {
  init() {
    const args = JSON.parse(readFileSync(arg0, 'utf8'))
    if (!args.question || !args.today) throw new Error('args need question and today')
    const S = { args, MAX: args.depth === 'max', plan: null, claims: [], sources: {}, sourceCounter: 0, claimCounter: 0, entries: [], voices: [], numbers: [], timeline: [], dossiers: [], parked: [], swarmed: {}, swarmedNames: [], seenSubq: [], reviewLog: [], round: 0, queue: [], carryEntries: [], pendingSwarms: [], pendingFollowups: [], outline: null, sections: [], front: null, verifyTag: '' }
    save(S)
    const B = blocks(S)
    const scoutAngles = ['the official/primary-source view: who the authorities are, what the canonical documents and datasets are, how the field defines its terms', 'the practitioner/community view: which forums, subreddits, Discourse boards, GitHub repos, Discord archives and YouTube channels practitioners use, and the insider vocabulary they use', 'the contrarian/critical view: who disputes the mainstream take, what the known failure modes and controversies are, what adjacent fields say']
    scoutAngles.forEach((a, i) => emit(`scout-${i + 1}`, `You are an orienting scout for a deep research project.
QUESTION: ${args.question}
${args.context ? `CONTEXT FROM THE USER: ${args.context}` : ''}
${B.OBJECTIVE_NOTE}
${B.EXAMPLES_NOTE}
Your angle: ${a}.
${B.TOOLS_NOTE}
Run at least 8 varied searches and open at least 8 pages. Map the landscape from your angle so the planner can decompose the question well. Do not try to answer the question.`, ORIENT))
    flushEmitted('scouts')
  },
  plan() {
    const S = load(), B = blocks(S), args = S.args
    const scouts = [1, 2, 3].map(i => readOut(`scout-${i}`)).filter(Boolean)
    emit('plan', `You are planning a deep research project.

QUESTION: ${args.question}
${args.context ? `CONTEXT FROM THE USER: ${args.context}` : ''}
${B.OBJECTIVE_NOTE}
${B.EXAMPLES_NOTE}

Scout reports:
${scouts.map((s, i) => `--- Scout ${i + 1} ---\n${s.landscape}\nInsider terms: ${(s.insider_terms || []).join(', ')}\nKey entities: ${(s.key_entities || []).join(', ')}\nCommunities: ${(s.communities || []).join(', ')}\nData lives at: ${(s.where_the_data_lives || []).join(', ')}`).join('\n\n')}

${B.TOOLS_NOTE}
${B.EXAMPLES.length ? `
Anti-anchoring rules:
- At most ONE sub-question may be about the given example(s) specifically.
- Include a sub-question that maps the whole landscape (enumerate the other members of the category).
- Include a sub-question on how instances differ and on counter-examples that break the pattern.
- Search angles must use category-level terms, not only the example's name.
` : ''}
Break the question into ${S.MAX ? '10-14' : '8-10'} sub-questions that together fully answer it with minimal overlap. Give each a short id like SQ1, SQ2.
Include sub-questions for: definitions/scope; the core facts; quantitative data; the strongest counter-evidence or opposing view; recent developments; practical implications; at least ${S.MAX ? 2 : 1} on what practitioners say in forums and communities (experiences, complaints, workarounds, hidden alternatives); one deliberately lateral angle (adjacent field, unconventional framing).${args.objective ? '\nSince the user has an objective, include a sub-question that surveys the realistic options/approaches for achieving it and one on how people who tried each option fared.' : ''}
For each, list 4-6 concrete search angles: specific queries including insider vocabulary, specific sites/communities/databases, specific document types.`, PLAN)
    flushEmitted('plan')
  },
  'absorb-plan'() {
    const S = load(); const plan = readOut('plan'); if (!plan) throw new Error('no plan output')
    plan.subquestions = plan.subquestions.map((sq, i) => ({ ...sq, id: (sq.id || `SQ${i + 1}`).replace(/[^A-Za-z0-9-]/g, '') }))
    S.plan = plan; S.queue = plan.subquestions; save(S)
    console.log(`PLAN ${plan.subquestions.length} sub-questions; field: ${plan.field}`)
    plan.subquestions.forEach(sq => console.log(`  ${sq.id}: ${sq.question}`))
  },
  research() {
    const S = load(), B = blocks(S), k = K(S)
    if (!S.queue.length) { console.log('NONE research (empty queue)'); return }
    S.round++; S.queue.forEach(sq => S.seenSubq.push(sq.question)); save(S)
    const MANDATES = { primary: "PRIMARY/OFFICIAL mandate: official documentation, standards, filings, datasets, papers, original announcements, the authors' own words. Establish the documented facts and numbers.", community: 'COMMUNITY mandate: what practitioners and real users say. Mine Reddit, Hacker News, Stack Exchange, GitHub issues/discussions, Discourse forums, Discord archives, YouTube, review sites, niche blogs. Capture experiences, complaints, workarounds, alternatives, insider vocabulary, dissent, and many verbatim voices.', contrarian: 'CONTRARIAN mandate: hunt the strongest counter-evidence. Who disagrees, what failed, what the mainstream take omits, rebuttals, retractions, "this is wrong because", people who tried it and regretted it, adjacent fields that see it differently.' }
    for (const sq of S.queue) for (const m of ['primary', 'community', 'contrarian']) emit(`research-r${S.round}-${sq.id}-${m}`, `You are one of three researchers on sub-question ${sq.id} of a deep research investigation into:
"${S.plan.restated_question}"
${B.OBJECTIVE_NOTE}
${B.EXAMPLES.length ? `The user's example(s) (${B.EXAMPLES.join('; ')}) only illustrate the category; unless your sub-question is about them, cover the broader set.` : ''}

SUB-QUESTION: ${sq.question}
${sq.why ? `Why it matters: ${sq.why}` : ''}
Starting angles: ${(sq.search_angles || []).join(' | ')}

${MANDATES[m]}

${B.TOOLS_NOTE}

${B.SOURCE_RULES}

${B.LEAD_RULES}
${m === 'community' ? `\n${B.FORUM_RULES}\n\n${B.PLATFORM_RECIPES}` : ''}

Standards: run at least ${k.MIN_SEARCHES} distinct searches (list them in searches_run), open and read at least ${k.MIN_SOURCES} distinct sources in full (list every URL in sources_read), return at least 10 claims with verbatim quotes. Mark key=true on claims the final answer or a recommendation depends on. Capture numbers and dated events. Note contradictions between sources.`, FINDINGS)
    flushEmitted(`research round ${S.round}`)
  },
  'absorb-research'() {
    const S = load(), B = blocks(S), k = K(S), final = flag('--final')
    const roundEntries = []
    for (const sq of S.queue) {
      const names = ['primary', 'community', 'contrarian'].map(m => `research-r${S.round}-${sq.id}-${m}`)
      expectOuts(names)
      const parts = names.map(readOut)
      const second = readOut(`research-r${S.round}-${sq.id}-second`)
      let merged = mergeFindings([...parts, second])
      if (!merged) { console.log(`EMPTY ${sq.id}`); continue }
      const hosts = new Set((merged.sources_read || []).map(host).filter(Boolean))
      if (!final && !second && (merged.claims.length < 10 || hosts.size < 5)) {
        console.log(`THIN ${sq.id}: ${merged.claims.length} claims, ${hosts.size} hosts`)
        emit(`research-r${S.round}-${sq.id}-second`, `Second-pass researcher. The first pass on this sub-question was thin (${merged.claims.length} claims from ${hosts.size} distinct sites).
QUESTION: "${S.plan.restated_question}"
SUB-QUESTION ${sq.id}: ${sq.question}
Already read (do NOT repeat these URLs): ${[...new Set(merged.sources_read)].join(', ')}
Already found: ${merged.claims.map(c => c.claim).join(' | ')}
${B.TOOLS_NOTE}
${B.SOURCE_RULES}
${B.LEAD_RULES}
${B.PLATFORM_RECIPES}
Find what they missed: new sites, new phrasings, insider vocabulary, other communities, primary documents. At least ${k.MIN_SEARCHES} searches, ${k.MIN_SOURCES} new sources, 10 new claims.`, FINDINGS)
        continue
      }
      if (final) { const e = absorb(S, merged, { kind: 'subquestion', ref: sq.id, question: sq.question, round: S.round, depth: 0 }); if (e) roundEntries.push(e) }
    }
    if (!final) { flushEmitted('second passes'); if (!emitted.length) console.log('Run with --final to absorb.'); return }
    S.roundEntries = roundEntries.map(e => e.id); save(S)
    console.log(`ABSORBED round ${S.round}: ${roundEntries.length} sub-questions, ${S.claims.filter(c => c.status === 'pending').length} pending claims, total ${S.claims.length}`)
  },
  triage() {
    const S = load(), B = blocks(S), k = K(S)
    const newEntries = S.entries.filter(e => S.roundEntries.includes(e.id) || S.carryEntries.includes(e.id))
    const byKey = new Map()
    for (const e of newEntries) for (const l of e.leads || []) {
      const kk = entityKey(l); const nm = (l.name || '').toLowerCase().trim()
      if (S.swarmed[kk] || S.swarmedNames.includes(nm)) continue
      const prev = byKey.get(kk)
      if (!prev) byKey.set(kk, { ...l, key: kk, reporters: [e.id], found_in: l.found_in || [], depth: e.depth || 0 })
      else { prev.reporters.push(e.id); prev.mention_count = (prev.mention_count || 1) + (l.mention_count || 1); prev.contested = prev.contested || l.contested; if (l.relevance === 'central') prev.relevance = 'central'; prev.depth = Math.min(prev.depth, e.depth || 0) }
    }
    for (const l of byKey.values()) { let s = 0; if (new Set(l.reporters).size >= 2) s += 3; if (l.relevance === 'central') s += 2; else if (l.relevance === 'supporting') s += 1; if (l.contested) s += 2; if ((l.mention_count || 0) >= 3) s += 1; if (['thread', 'community', 'tool', 'document', 'business_idea'].includes(l.entity_type)) s += 1; if (l.hops_taken === 0) s += 1; l.prescore = s }
    const leads = [...byKey.values()].sort((a, b) => b.prescore - a.prescore)
    S.leads = leads; save(S)
    if (!leads.length) { console.log('NONE triage'); return }
    const swarmCap = Math.max(0, Math.min(k.SWARMS_PER_ROUND, k.MAX_SWARMS - Object.keys(S.swarmed).length))
    emit(`triage-r${S.round}`, `You are the lead triage officer for a deep research investigation into:
"${S.plan.restated_question}"
${B.OBJECTIVE_NOTE}

Researchers found the leads below (entities they noticed but did not exhaust). For each decide:
- "swarm": worth ${S.MAX ? '8-12' : '5-6'} dedicated agents that will read EVERYTHING about it. Use this when the entity could change the answer or a recommendation, when several researchers independently hit it, when sources disagree about it, when it is a container with real depth (a long thread, a tool with its own ecosystem, a study many cite, a candidate business idea that needs its customers, incumbents, economics and founder reports mapped), or when insiders treat it as common knowledge the outside literature ignores.
- "followup": one agent, one or two hops, to pin down a specific fact.
- "park": record as unexplored; not worth the effort now.
Rules: pre-scores >= 6 may not be parked. Leads at depth >= ${k.MAX_DEPTH} may not be swarmed (followup or park only). At most ${swarmCap} swarms this round; prefer diversity over many leads about the same thing. Copy each lead's key EXACTLY. For every non-parked lead write 3-8 concrete questions the agents must answer about it.

LEADS (key | pre-score | type | name | url | reporters | mentions | relevance | contested | hops | depth | unknowns):
${leads.map(l => `${l.key} | score ${l.prescore} | ${l.entity_type} | ${l.name} | ${l.canonical_url || '-'} | reporters ${[...new Set(l.reporters)].join(',')} | mentions ${l.mention_count} | ${l.relevance} | contested ${!!l.contested} | hops ${l.hops_taken} | depth ${l.depth} | unknown: ${l.what_is_unknown}`).join('\n')}
Already swarmed (do not repeat): ${Object.values(S.swarmed).map(v => v.name).join(', ') || 'none'}`, TRIAGE)
    flushEmitted(`triage round ${S.round} (${leads.length} leads, cap ${swarmCap} swarms)`)
  },
  'absorb-triage'() {
    const S = load(), B = blocks(S), k = K(S)
    const triage = readOut(`triage-r${S.round}`) || { decisions: [] }
    const leadByKey = new Map((S.leads || []).map(l => [l.key, l]))
    const decisions = triage.decisions.filter(d => leadByKey.has(d.key))
    const decided = new Set(decisions.map(d => d.key))
    S.leads.filter(l => !decided.has(l.key) && l.prescore >= 6).forEach(l => decisions.push({ key: l.key, tier: 'followup', why: 'script floor: high pre-score left undecided', questions_to_answer: [l.what_is_unknown] }))
    const swarmCap = Math.max(0, Math.min(k.SWARMS_PER_ROUND, k.MAX_SWARMS - Object.keys(S.swarmed).length))
    const names = new Set()
    const swarmDecisions = decisions.filter(d => { const l = leadByKey.get(d.key); const nm = (l.name || '').toLowerCase().trim(); if (d.tier !== 'swarm' || l.depth >= k.MAX_DEPTH || names.has(nm)) return false; names.add(nm); return true }).slice(0, swarmCap)
    const followups = decisions.filter(d => d.tier === 'followup' || (d.tier === 'swarm' && !swarmDecisions.includes(d)))
    decisions.filter(d => d.tier === 'park').forEach(d => S.parked.push({ ...leadByKey.get(d.key), why_parked: d.why, round: S.round }))
    S.leads.filter(l => !decided.has(l.key) && l.prescore < 6).forEach(l => S.parked.push({ ...l, why_parked: 'not selected by triage', round: S.round }))
    S.pendingSwarms = []; S.pendingFollowups = []
    for (const d of swarmDecisions) {
      const lead = leadByKey.get(d.key); const angles = anglesFor(S, lead.entity_type); const depth = (lead.depth || 0) + 1
      S.swarmCounter = (S.swarmCounter || 0) + 1; const swarmId = `SW${S.swarmCounter}`
      S.swarmed[lead.key] = { name: lead.name, entity_type: lead.entity_type, depth, round: S.round, agents: angles.length + 1, swarmId }
      S.swarmedNames.push((lead.name || '').toLowerCase().trim())
      S.pendingSwarms.push({ swarmId, lead, depth, angles: angles.map(a => a[0]), questions: d.questions_to_answer || [] })
      const questions = (d.questions_to_answer || []).map(q => `- ${q}`).join('\n')
      for (const [angle, brief] of angles) emit(`swarm-${swarmId}-${angle}`, `You are one agent in a deep-dive swarm investigating the ${lead.entity_type} "${lead.name}" for a research project on:
"${S.plan.restated_question}"
${B.OBJECTIVE_NOTE}
ENTITY: ${lead.name}${lead.canonical_url ? ` — ${lead.canonical_url}` : ''}
Why it matters: ${lead.lead}
What is unknown about it: ${lead.what_is_unknown || 'see questions'}
Questions this swarm must answer:
${questions || '- what exactly it is, who says what, what the evidence is, how it relates to the main question, what contradicts it'}

YOUR ANGLE (${angle}): ${brief}
Other agents cover the other angles; go deep on yours. Set "angle" in your output to "${angle}".

${B.TOOLS_NOTE}
${B.FORUM_RULES}
${B.PLATFORM_RECIPES}
${B.SOURCE_RULES}
${B.LEAD_RULES}

Exhaustive coverage of your angle, not a summary. Fetch at least 10 pages (list them in sources_read). Return at least 8 claims with verbatim quotes (key=true where the main question or a recommendation depends on them), recurring_claims with distinct-user counts, 10-30 voices with credibility signals, every number, contradictions and who had the better of each argument, new leads, and an exact coverage_note. In answers[], answer each swarm question from your angle's evidence.`, SWARM_FINDINGS)
    }
    followups.forEach((d, i) => {
      const l = leadByKey.get(d.key); const id = `FU-r${S.round}-${i + 1}`
      S.pendingFollowups.push({ id, lead: l })
      emit(`followup-${id}`, `Follow-up researcher on a lead found during research into "${S.plan.restated_question}".
LEAD: ${l.name} (${l.entity_type})${l.canonical_url ? ` — ${l.canonical_url}` : ''}
Why: ${l.lead}
Questions to answer:
${(d.questions_to_answer || []).map(q => `- ${q}`).join('\n')}
${B.TOOLS_NOTE}
${B.SOURCE_RULES}
${B.LEAD_RULES}
${B.PLATFORM_RECIPES}
Two hops max, but thorough on those hops: open at least 6 sources, return every claim with quotes, voices, numbers, and any new leads.`, FINDINGS)
    })
    save(S)
    console.log(`TRIAGE r${S.round}: ${swarmDecisions.length} swarms (${swarmDecisions.map(d => leadByKey.get(d.key).name).join('; ')}), ${followups.length} follow-ups, ${S.parked.filter(p => p.round === S.round).length} parked`)
    flushEmitted('swarm + followup agents')
  },
  'absorb-swarms'() {
    const S = load()
    const carry = []
    for (const sw of S.pendingSwarms) {
      const names = sw.angles.map(a => `swarm-${sw.swarmId}-${a}`); expectOuts(names)
      const results = names.map(readOut).filter(Boolean)
      sw.results = results.length
      for (const r of results) { const e = absorb(S, r, { kind: 'swarm', ref: `${sw.swarmId}:${r.angle || 'angle'}`, question: `Deep dive: ${sw.lead.name} (${r.angle})`, round: S.round, entity: sw.lead.name, depth: sw.depth }); if (e) carry.push(e.id) }
      if (results.length) emit(`dossier-${sw.swarmId}`, `You are the dossier compiler for the ${sw.lead.entity_type} "${sw.lead.name}". Below are the reports of ${results.length} swarm agents, each from a different angle. Synthesise ONE dossier: what it is (400-1000 words), consensus claims, dissent, primary sources, credibility assessment, how it relates to the question "${S.plan.restated_question}", open questions, and recommended follow-up leads (structured). Do not add facts not in the reports. Set name to "${sw.lead.name}" and entity_type to "${sw.lead.entity_type}".

${results.map(r => `=== Angle: ${r.angle} ===\n${r.summary}\nAnswers: ${(r.answers || []).map(a => `${a.question} -> ${a.answer}`).join(' | ')}\nRecurring: ${(r.recurring_claims || []).map(x => `${x.claim} (+${x.supporters}/-${x.dissenters})`).join('; ')}\nContradictions: ${(r.contradictions || []).join('; ')}\nCoverage: ${r.coverage_note}`).join('\n\n')}`, DOSSIER)
    }
    for (const fu of S.pendingFollowups) {
      const f = readOut(`followup-${fu.id}`); if (!f) { console.log(`MISSING followup-${fu.id}`); continue }
      const e = absorb(S, f, { kind: 'followup', ref: fu.id, question: `Follow-up: ${fu.lead.name}`, round: S.round, entity: fu.lead.name, depth: (fu.lead.depth || 0) + 1 }); if (e) carry.push(e.id)
    }
    S.carryEntries = carry; save(S)
    console.log(`SWARMS absorbed: ${S.pendingSwarms.map(s => `${s.swarmId} ${s.results}/${s.angles.length}`).join(', ') || 'none'}; followups ${S.pendingFollowups.length}; pending claims ${S.claims.filter(c => c.status === 'pending').length}`)
    flushEmitted('dossiers')
  },
  'absorb-dossiers'() {
    const S = load()
    for (const sw of S.pendingSwarms) {
      const d = readOut(`dossier-${sw.swarmId}`); if (!d) { console.log(`MISSING dossier-${sw.swarmId}`); continue }
      S.dossiers.push({ ...d, swarm_id: sw.swarmId, depth: sw.depth })
      const e = { id: `${sw.swarmId}:dossier`, kind: 'dossier', round: S.round, depth: sw.depth, entity: sw.lead.name, question: '', summary: d.one_paragraph, claim_ids: [], unanswered: d.open_questions || [], contradictions: [], leads: (d.recommended_followups || []).filter(l => l && l.name) }
      S.entries.push(e); S.carryEntries.push(e.id)
    }
    save(S); console.log(`DOSSIERS ${S.dossiers.length} total`)
  },
  quotecheck() {
    const S = load(), B = blocks(S), k = K(S)
    const pending = S.claims.filter(c => c.status === 'pending')
    S.verifyTag = arg0 || `r${S.round}`; save(S)
    chunk(pending, k.CHUNK).forEach((ch, i) => emit(`quotecheck-${S.verifyTag}-${i}`, `You are a citation checker. For each claim below: open the URL (if blocked, try Wayback https://web.archive.org/web/2/<url>, archive.ph, or https://r.jina.ai/<url>, and record archive_url_used). Report whether the quote exists on the page verbatim/near-verbatim, whether the page actually supports the claim (not out of context), and the page date. Be strict: your job is to catch overstated or fabricated citations. Never mark a page you could not open as supporting anything. Check ALL ${ch.length} claims; return one entry per claim_id.
${B.TOOLS_NOTE}

${ch.map(c => `${c.id}\n  claim: ${c.claim}\n  url: ${c.url}\n  quote: "${c.quote}"`).join('\n')}`, QUOTE_CHECKS))
    flushEmitted(`quotecheck ${pending.length} claims`)
  },
  'absorb-quotecheck'() {
    const S = load(), B = blocks(S), k = K(S)
    const pending = S.claims.filter(c => c.status === 'pending')
    const n = Math.ceil(pending.length / k.CHUNK)
    const names = Array.from({ length: n }, (_, i) => `quotecheck-${S.verifyTag}-${i}`); expectOuts(names)
    const checks = new Map(names.map(readOut).filter(Boolean).flatMap(r => r.checks || []).map(x => [x.claim_id, x]))
    for (const c of pending) {
      const x = checks.get(c.id); if (!x) { c.notes.push('quote-check: no result'); continue }
      if (x.page_date && !c.published) c.published = x.page_date
      if (x.archive_url_used) c.access_note = `via ${x.archive_url_used}`
      if (!x.reachable || x.quote_found === 'not_found' || x.supports_claim === 'no' || x.supports_claim === 'out_of_context') { c.status = 'citation_failed'; c.notes.push(`quote-check: reachable=${x.reachable}, quote=${x.quote_found}, supports=${x.supports_claim}${x.note ? ' — ' + x.note : ''}`) }
      else if (x.quote_found === 'paraphrase_only' || x.supports_claim === 'partially') c.notes.push(`quote-check: ${x.quote_found}, supports=${x.supports_claim}${x.note ? ' — ' + x.note : ''}`)
    }
    const failed = pending.filter(c => c.status === 'citation_failed')
    S.resourceIds = failed.map(c => c.id); save(S)
    chunk(failed, k.CHUNK).forEach((ch, i) => emit(`resource-${S.verifyTag}-${i}`, `You are a re-sourcer. These claims failed citation checks (the URL did not support them or the quote was not found). For each, find a URL that genuinely supports the claim with a verbatim quote, or report that you could not. Return findings with one claim per input claim (same wording), each with its new url/quote/title; omit claims you could not source. Put the input claim id at the start of each claim text in square brackets, e.g. "[C0012] ...".
${B.TOOLS_NOTE}
${B.SOURCE_RULES}
${ch.map(c => `${c.id}: ${c.claim} (failed source: ${c.url})`).join('\n')}`, FINDINGS))
    console.log(`QUOTECHECK: ${failed.length} failed of ${pending.length}; ${statLine(S)}`)
    flushEmitted('re-source')
  },
  'absorb-resource'() {
    const S = load(), k = K(S)
    const failedIds = new Set(S.resourceIds || [])
    const n = Math.ceil(failedIds.size / k.CHUNK)
    const fixes = Array.from({ length: n }, (_, i) => readOut(`resource-${S.verifyTag}-${i}`)).filter(Boolean).flatMap(r => r.claims || [])
    let fixed = 0
    for (const f of fixes) {
      const m = (f.claim || '').match(/^\[(C\d{4})\]\s*/); const c = m && failedIds.has(m[1]) && claimById(S, m[1])
      if (!c || !f.url || !f.quote) continue
      const s = addSource(S, f); if (!s) continue
      c.notes.push(`re-sourced from ${c.url}`); Object.assign(c, { url: f.url, quote: f.quote, title: f.title || f.url, source_type: f.source_type || c.source_type, published: f.published || c.published, sid: s.id, status: 'pending' }); s.claim_ids.push(c.id); fixed++
    }
    save(S); console.log(`RESOURCED ${fixed}/${failedIds.size}`)
  },
  skeptics() {
    const S = load(), B = blocks(S), k = K(S)
    const passed = S.claims.filter(c => c.status === 'pending')
    const toJudge = passed.filter(c => c.key || c.source_type === 'community')
    passed.filter(c => !toJudge.includes(c)).forEach(c => { c.status = 'source_checked' })
    S.judgeIds = toJudge.map(c => c.id); save(S)
    chunk(toJudge, k.JUDGE_CHUNK).forEach((ch, i) => { for (let j = 0; j < k.SKEPTICS; j++) emit(`skeptic-${S.verifyTag}-${i}-${j + 1}`, `You are fact-checker #${j + 1} of ${k.SKEPTICS} on research into "${S.plan.restated_question}". Your job is to REFUTE the claims below, not to agree with them.
${B.TOOLS_NOTE}
For each claim: search for INDEPENDENT sources (not copies of the same original) that confirm or contradict it; check whether it is outdated as of today. Mark "confirmed" only with independent support (for community claims: several independent users or a primary source saying the same thing; a single anecdote is "unclear"). Mark "refuted" when independent evidence contradicts it, "outdated" when it was true but no longer is. Give the evidence_url for every verdict. Check ALL ${ch.length} claims; a missing claim_id counts against you.

${ch.map(c => `${c.id} [${c.source_type}${c.published ? ', ' + c.published : ''}] ${c.claim}\n  source: ${c.url}\n  quote: "${c.quote}"`).join('\n')}`, VERDICTS) })
    console.log(`SKEPTICS: ${toJudge.length} key/community claims; ${passed.length - toJudge.length} source-checked only`)
    flushEmitted('skeptic panels')
  },
  'absorb-skeptics'() {
    const S = load(), B = blocks(S), k = K(S)
    const toJudge = (S.judgeIds || []).map(id => claimById(S, id)).filter(Boolean)
    const chunks = chunk(toJudge, k.JUDGE_CHUNK)
    const needAdj = []
    chunks.forEach((ch, i) => {
      const votes = Array.from({ length: k.SKEPTICS }, (_, j) => readOut(`skeptic-${S.verifyTag}-${i}-${j + 1}`)).filter(Boolean).flatMap(p => p.verdicts || [])
      for (const c of ch) {
        const vs = votes.filter(v => v.claim_id === c.id)
        vs.forEach(v => c.notes.push(`${v.status}: ${v.note}${v.evidence_url ? ` (${v.evidence_url})` : ''}`))
        if (!vs.length) { c.status = 'source_checked'; c.notes.push('no skeptic verdicts returned'); continue }
        const count = s => vs.filter(v => v.status === s).length
        const top = ['refuted', 'outdated', 'confirmed', 'unclear'].map(s => [s, count(s)]).sort((a, b) => b[1] - a[1])[0]
        if (top[1] === vs.length && vs.length >= 2 && top[0] !== 'unclear') c.status = top[0]; else needAdj.push(c)
      }
    })
    S.adjIds = needAdj.map(c => c.id); save(S)
    chunk(needAdj, k.JUDGE_CHUNK).forEach((ch, i) => emit(`adjudicate-${S.verifyTag}-${i}`, `You are the adjudicator. Fact-checkers split on the claims below. Read their notes, open at least one independent source per claim yourself, and return a decisive status: confirmed, refuted, outdated, or unclear (only if the evidence genuinely cannot settle it). Give evidence_url and a note explaining the decision. Return one verdict per claim_id.
${B.TOOLS_NOTE}
${ch.map(c => `${c.id}: ${c.claim}\n  source: ${c.url} — "${c.quote}"\n  votes: ${c.notes.join(' | ')}`).join('\n\n')}`, VERDICTS))
    console.log(`SKEPTICS absorbed: ${needAdj.length} split of ${toJudge.length}; ${statLine(S)}`)
    flushEmitted('adjudication')
  },
  'absorb-adjudicate'() {
    const S = load(), k = K(S)
    const need = (S.adjIds || []).map(id => claimById(S, id)).filter(Boolean)
    const n = Math.ceil(need.length / k.JUDGE_CHUNK)
    const byId = new Map(Array.from({ length: n }, (_, i) => readOut(`adjudicate-${S.verifyTag}-${i}`)).filter(Boolean).flatMap(r => r.verdicts || []).map(v => [v.claim_id, v]))
    for (const c of need) { const v = byId.get(c.id); if (v) { c.status = v.status === 'unclear' ? 'contested' : v.status; c.notes.push(`adjudicator: ${v.status} — ${v.note}${v.evidence_url ? ` (${v.evidence_url})` : ''}`) } else c.status = 'contested' }
    S.claims.filter(c => c.status === 'pending').forEach(c => { c.status = 'source_checked'; c.notes.push('left pending after verification; treated as source-checked') })
    save(S); console.log(`VERIFIED: ${S.claims.length} claims; ${statLine(S)}; ${Object.keys(S.sources).length} sources; ${S.voices.length} voices; ${Object.keys(S.swarmed).length} swarms`)
  },
  direct() {
    const S = load(), B = blocks(S), k = K(S)
    if (S.round >= k.MAX_ROUNDS) { console.log('STOP max rounds reached'); return }
    const compact = S.claims.map(claimLine).join('\n')
    const digest = S.entries.filter(e => e.kind !== 'dossier').map(e => `## ${e.id} (${e.kind}, r${e.round}): ${e.question}\n${(e.summary || '').slice(0, 1500)}\nUnanswered: ${e.unanswered.join('; ') || 'none'}\nContradictions: ${e.contradictions.join('; ') || 'none'}`).join('\n\n')
    const dossierDigest = S.dossiers.map(d => `- ${d.name} (${d.entity_type}): ${d.one_paragraph}\n  open: ${(d.open_questions || []).join('; ')}`).join('\n')
    const common = `Investigation: "${S.plan.restated_question}"
${B.OBJECTIVE_NOTE}
${B.EXAMPLES_NOTE}
Today: ${S.args.today}. Round ${S.round} of at most ${k.MAX_ROUNDS} is complete (minimum ${k.MIN_ROUNDS}).

SUB-QUESTIONS RESEARCHED SO FAR (do not propose anything overlapping >50% with these):
${S.seenSubq.map(q => `- ${q}`).join('\n')}

ENTITY DOSSIERS:
${dossierDigest || 'none yet'}

FINDINGS DIGEST:
${digest}

CLAIM LEDGER (id [status] [source type, date] claim — source):
${compact}`
    emit(`director-r${S.round}`, `You are the research director.
${common}

Decide what to research next so the final answer is complete and trustworthy. Consider: unanswered items; refuted/contested/citation-failed claims that need better evidence; missing counter-evidence; missing quantitative data; missing recent developments; perspectives and communities not yet represented; dots that connect across sub-questions and dossiers (if two findings together suggest something new, investigate it).${B.EXAMPLES.length ? " Check for anchoring on the user's example(s) and broaden if needed." : ''}${S.args.objective ? ' The user needs 15-20 concrete, well-evidenced options; if fewer candidate ideas have dossiers, propose sub-questions that surface and evidence more candidates.' : ''}
Rate coverage on each dimension. Return up to ${S.MAX ? 8 : 5} NEW sub-questions (ids like D1, D2) with 4-6 concrete search angles each. Set done=true only if every dimension is at least adequate and nothing material is missing.`, GAPS)
    emit(`stopaudit-r${S.round}`, `You are the stop auditor. Your job is to argue that this research is NOT done. A hostile expert reviewer in the field "${S.plan.field}" will read the final report: list everything they would say is missing, thin, one-sided, outdated or unverified, and turn the most important gaps into up to ${S.MAX ? 6 : 4} new sub-questions (ids like A1, A2) with concrete search angles. Rate coverage honestly on each dimension. Set done=true only if you genuinely cannot find a material gap.
${common}`, GAPS)
    flushEmitted('director + stop auditor')
  },
  'absorb-direct'() {
    const S = load(), k = K(S)
    const director = readOut(`director-r${S.round}`), auditor = readOut(`stopaudit-r${S.round}`)
    const norm = s => (s || '').toLowerCase().replace(/[^a-z0-9 ]+/g, ' ').split(/\s+/).filter(w => w.length > 3)
    const overlaps = (a, b) => { const A = new Set(norm(a)), Bs = new Set(norm(b)); const inter = [...A].filter(w => Bs.has(w)).length; return inter / Math.max(1, Math.min(A.size, Bs.size)) > 0.5 }
    const proposed = [...(director ? director.new_subquestions || [] : []), ...(auditor ? auditor.new_subquestions || [] : [])]
    const fresh = []
    for (const sq of proposed) if (sq && sq.question && !S.seenSubq.some(q => overlaps(q, sq.question)) && !fresh.some(f => overlaps(f.question, sq.question))) fresh.push(sq)
    S.queue = fresh.map((sq, i) => ({ ...sq, id: `R${S.round + 1}-${i + 1}` }))
    const thin = g => g && Object.values(g.coverage_assessment || {}).some(v => v === 'thin')
    const bothDone = director && auditor && director.done && auditor.done && !thin(director) && !thin(auditor)
    console.log(`DIRECT r${S.round}: director done=${director ? director.done : 'n/a'} (${director ? JSON.stringify(director.coverage_assessment) : ''}); auditor done=${auditor ? auditor.done : 'n/a'} (${auditor ? JSON.stringify(auditor.coverage_assessment) : ''}); ${S.queue.length} new sub-questions; ${S.carryEntries.length} entries carrying leads`)
    S.queue.forEach(sq => console.log(`  ${sq.id}: ${sq.question}`))
    let verdict = 'CONTINUE'
    if (S.round >= k.MIN_ROUNDS && bothDone && !S.queue.length) verdict = 'STOP'
    if (!S.queue.length && !S.carryEntries.length) { if (S.round < k.MIN_ROUNDS) S.queue = [{ id: `R${S.round + 1}-1`, question: `What important aspects of "${S.plan.restated_question}" has the research so far missed? Find them.`, search_angles: ['lateral searches', 'adjacent fields', 'newest sources', 'communities not yet covered'] }]; else verdict = 'STOP' }
    if (S.round >= k.MAX_ROUNDS) verdict = 'STOP'
    S.unresearched = verdict === 'STOP' ? S.queue.map(q => q.question) : []
    save(S); console.log(verdict)
  },
  outline() {
    const S = load(), B = blocks(S), k = K(S)
    const skeleton = `Required skeleton (instantiate all; add theme sections as needed; split any section whose claim_ids exceed ~40):
1. scope — Scope, definitions and the question as researched (assumptions, exclusions, examples vs category) — 600+ words
2. landscape — Landscape / background (the field, the players, the history to today) — 1500+
3+. theme-* — one section per theme (typically ${S.MAX ? '7-10' : '5-8'}; 1200-2500 words each): every relevant confirmed claim, contested ones labelled, community voices inline, a table wherever 4+ items compare
then. deep-* — one section per entity dossier whose relation_to_question is not tangential (800-2000 words each)${S.args.objective ? '; for candidate business ideas each deep-* section must cover: target customer and pain, why now, acquisition channel with proof, unit economics and pricing, time to first revenue, what $25k-$50k buys, risks and failure modes, 2-3 existing players' : ''}
then. quant — Quantitative picture (every number with date, source, whether challenged; tables) — 800+
then. disagreements — Where the evidence disagrees, and why — 1000+
then. debunked — Debunked, outdated and unverifiable claims — 800+
then. practitioners — What practitioners say: community evidence by community, with spread and era — 1200+
${S.args.objective ? 'then. recommendations — Ranked options table, then one subsection per option (pros, cons, cost/effort, risks, prerequisites, who it suits, evidence IDs), "if you only do one thing", next steps — 1500+\n' : ''}then. trail — Discovery trail: how one lead led to another, what the swarms found that the plan did not anticipate — 800+
then. unknowns — Unknowns and open leads — 600+
then. confidence — Confidence assessment per major conclusion — 500+
Total body minimum: ${k.MIN_BODY_WORDS} words. Distribute min_words/target_words so the sum of target_words is at least ${Math.round(k.MIN_BODY_WORDS * 1.15)}. Executive summary and glossary are written separately; do not include them. Use short lowercase ids with hyphens.`
    emit('outline', `You are the outline editor for a very long, exhaustive research report on:
"${S.plan.restated_question}"
${B.OBJECTIVE_NOTE}
${B.EXAMPLES_NOTE}

${skeleton}

Assign EVERY claim id below to at least one section (a claim may appear in several). Theme sections should group claims by subject, not by which sub-question found them. For each section give purpose, must_cover (3+ items), required tables, dossier_names it should draw on (exact names), a voice_filter, min_words and target_words.

ENTITY DOSSIERS: ${S.dossiers.map(d => `${d.name} (${d.entity_type}; relation: ${(d.relation_to_question || '').slice(0, 200)})`).join(' | ') || 'none'}
SUB-QUESTIONS: ${S.entries.filter(e => e.kind === 'subquestion').map(e => `${e.id}: ${e.question}`).join(' | ')}
VOICES available: ${S.voices.length}; NUMBERS: ${S.numbers.length}; TIMELINE entries: ${S.timeline.length}

CLAIM LEDGER:
${usable(S).map(claimLine).join('\n')}`, OUTLINE)
    flushEmitted('outline')
  },
  'absorb-outline'() {
    const S = load(); const outline = readOut('outline'); if (!outline) throw new Error('no outline')
    outline.sections = outline.sections.map(s => ({ ...s, id: slug(s.id || s.title) }))
    const assigned = new Set(outline.sections.flatMap(s => s.claim_ids || []))
    const orphans = usable(S).filter(c => !assigned.has(c.id)).map(c => c.id)
    if (orphans.length) { const tgt = outline.sections.find(s => /theme/i.test(s.id)) || outline.sections[1] || outline.sections[0]; tgt.claim_ids.push(...orphans); console.log(`ORPHANS ${orphans.length} -> ${tgt.id}`) }
    S.outline = outline; save(S)
    console.log(`OUTLINE ${outline.sections.length} sections, ${outline.sections.reduce((n, s) => n + (s.target_words || 0), 0)} target words`)
    outline.sections.forEach(s => console.log(`  ${s.id}: ${s.title} (${s.claim_ids.length} claims, min ${s.min_words})`))
    writePrompts(S)
  },
  'absorb-sections'() {
    const S = load(), final = flag('--final')
    S.sections = []
    for (const spec of S.outline.sections) {
      const a = readOut(`write-${spec.id}`), b = readOut(`expand-${spec.id}`)
      let s = a; if (b && wc(b.markdown) > wc(a ? a.markdown : '')) s = b
      if (!s) { console.log(`MISSING write-${spec.id}`); continue }
      const words = wc(s.markdown)
      if (!final && !b && words < 0.9 * spec.min_words) { console.log(`SHORT ${spec.id}: ${words}/${spec.min_words}`); writePrompts(S, spec, s); continue }
      S.sections.push({ id: spec.id, title: spec.title, markdown: s.markdown, word_count: words })
    }
    save(S)
    if (!final) { flushEmitted('expansions'); return }
    console.log(`SECTIONS ${S.sections.length}/${S.outline.sections.length}, ${S.sections.reduce((n, s) => n + s.word_count, 0)} body words`)
  },
  stitch() {
    const S = load(), B = blocks(S)
    emit('stitch', `You are the stitching editor of a very long research report on "${S.plan.restated_question}". ${B.OBJECTIVE_NOTE}
Write (1) an executive summary of 600-1000 words: the direct answer, overall confidence, the top findings with [S#] citations copied from the sections, the top recommendations if any (for a business-ideas report: the ranked shortlist in a table), the biggest unknowns; (2) a "How to read this report" section (300+ words) explaining the status labels, source types, [C####] claim ids (Appendix A), confidence scale, and the methodology in brief (${S.round} rounds, ${S.entries.filter(e => e.kind === 'subquestion').length} sub-questions, ${Object.keys(S.swarmed).length} deep-dive swarms, ${S.claims.length} claims verified); (3) a 2-3 sentence bridge for each section id; (4) a glossary of every insider term, acronym, tool and named entity used in the report, 1-3 sentences each with [S#] where a source defines it.
${B.STATUS_LEGEND}
Cite only with [S#] tokens that appear in the draft.

DRAFT:
${draftText(S.sections)}`, FRONT)
    flushEmitted('stitch')
  },
  'absorb-stitch'() { const S = load(); S.front = readOut('stitch'); save(S); console.log(S.front ? 'FRONT ok' : 'MISSING stitch') },
  review() {
    const S = load(), B = blocks(S), pass = Number(arg0 || 1)
    const draft = draftText(S.sections)
    const header = `Research question: "${S.plan.restated_question}"\n${B.OBJECTIVE_NOTE}\n${B.EXAMPLES_NOTE}\nToday: ${S.args.today}. Field: ${S.plan.field}.\nReturn concrete, locatable issues each with the offending text quoted verbatim (<= 60 words), the section_id (from the "{#id}" marker in the heading), and a proposed replacement text. Do not return praise. Severity: critical = false or unsupported statement a reader would act on; major = materially misleading, missing or incoherent; minor = clarity/precision; nit = style. Prefix issue ids with your lens name. Set "lens" to your lens name.\n${B.STATUS_LEGEND}`
    const cited = new Set((draft.match(/\[S\d+\]/g) || []).map(t => t.slice(1, -1)))
    const citedSources = sourceList(S).filter(s => cited.has(s.id))
    const U = usable(S)
    const lenses = [
      ['completeness', `You are the completeness reviewer. The ledger below is everything the team found; the report should use ALL of it that is relevant. List: confirmed/contested claims marked UNUSED that a reader would want (section + text to add); dossiers that got less than a full subsection; dissent, contradictions and refuted claims silently dropped (refuted ones should appear as debunked); numbers and timeline entries missing; sub-questions underrepresented relative to evidence volume; firsthand community voices not quoted anywhere. Major for any omission that changes understanding. The bar is exhaustive, not sufficient.\n\nLEDGER (UNUSED = neither the claim id nor its source token appears in the draft):\n${U.map(c => `${claimLine(c)}${draft.includes(c.id) || draft.includes(`[${c.sid}]`) ? '' : ' — UNUSED'}`).join('\n')}\nDOSSIERS: ${S.dossiers.map(d => d.name).join(', ') || 'none'}\nVOICES not quoted: ${S.voices.filter(v => !draft.includes((v.quote || '').slice(0, 40))).length} of ${S.voices.length}`],
      ['anchoring', `You are the anchoring and bias reviewer. Check whether the report over-focuses on the user's illustrative examples or on the first entities found; presents the loudest community's view as the field's view; lets one source or one swarm dominate a section; frames contested claims as settled or settled ones as contested; uses confidence language inconsistent with the status labels; treats vendor/marketing sources as neutral; omits the strongest counter-case. Propose rebalanced text with the claim ids that support it.`],
      ['logic', `You are the logic reviewer. Find conclusions not supported by the cited claims; non-sequiturs; recommendations whose pros/cons do not follow from the evidence; internal contradictions between sections; causal claims resting on correlation or anecdote; unstated assumptions; places where "users report X" silently becomes "X is true".`],
      ['structure', `You are the structure editor. The report must be long and detailed, so your job is NOT to shorten it. Find sections that duplicate each other (propose merging content, never deleting evidence); missing signposting; lists of 4+ comparable items that should be tables; inconsistent terminology; headings not matching content; walls of text needing subheadings; glossary terms used before definition. Never propose cutting evidence or quotes.`],
      ['expert', `You are a senior practitioner with 20 years in the field "${S.plan.field}", reviewing this as a peer who expects the author to be an outsider. Where would you object? What does it get subtly wrong, oversimplify, or miss that an insider would raise immediately (standard caveats, well-known failure modes, trade-offs, regulatory or operational realities, the thing everyone in the field knows but nobody writes down)? Which claims need a stronger source? Which recommendations are naive? Where the ledger lacks the evidence for your fix, set needs_research=true with the exact research_question.`],
      ['numbers', `You are the quantitative consistency reviewer. Check every number, date, version, price and percentage against the numbers table and claim quotes: same figure, unit, date; same quantity given differently in two sections; aged figures not dated; ranges reported as points; forum-reported numbers not labelled as such.\n\nNUMBERS TABLE:\n${S.numbers.map(n => `- ${n.what}: ${n.value} (${n.who || '?'}, ${n.date || 'undated'}${n.challenged ? ', CHALLENGED' : ''}) — ${n.url}`).join('\n')}`],
      ['recency', `You are the recency reviewer. Today is ${S.args.today}. For each key statement, check the dates of its sources and whether newer evidence in the ledger supersedes it; flag statements resting only on sources older than 18 months in a fast-moving area, and statements whose claims are marked outdated yet appear as current. Propose dated wording ("as of <date>") or replacement claims.\n\nCLAIM DATES:\n${U.map(c => `${c.id} [${c.status}] ${c.published || 'undated'}: ${(c.claim || '').slice(0, 120)}`).join('\n')}`],
      ['voices', `You are the community-evidence reviewer. For every statement attributed to users/forums: is it labelled as community evidence; does the report say how widespread it is (one user vs many, which communities, what era); are quotes verbatim and attributed with date; are dissenting voices represented alongside consensus; is any single anecdote inflated into a pattern; are the strongest firsthand quotes used where they would help?\n\nAVAILABLE VOICES:\n${S.voices.slice(0, 150).map(v => `- "${v.quote}" — ${v.author}, ${v.platform}, ${v.date || 'undated'}, ${v.stance}`).join('\n')}`],
      ...(S.args.objective ? [['recommendations', `You are the decision reviewer acting for the user, whose objective is: ${S.args.objective}. Are recommendations ranked with explicit criteria; does each have pros, cons, cost/effort, risks, prerequisites, who it suits and who it doesn't, and the claim ids behind it; are options the evidence supports missing; is there an "if you only do one thing" answer; are next steps concrete; does any recommendation rest on contested or refuted claims? For a business-ideas brief: does every idea have target customer, pain, why now, channel with proof, unit economics, time to first revenue, what the budget buys, risks, and named existing players?`]] : []),
    ]
    chunk(citedSources, 10).forEach((ch, i) => emit(`review${pass}-cite-${i}`, `${header}
You are a citation auditor (lens "citation"). For each source below: open the URL (Wayback/archive.ph/r.jina.ai if blocked), find every sentence in the draft that cites its token, and check whether the page actually supports each such sentence (not just the ledger quote taken out of context). Report an issue (critical for unsupported/out-of-context, major for partially supported or unreachable with no archive) for each failing sentence, with a proposed_fix that either softens the sentence to what the source supports or replaces the citation with another [S#] token from the draft that does support it. Never treat a source you could not open as supporting anything.
${B.TOOLS_NOTE}

SOURCES TO AUDIT:
${ch.map(s => `[${s.id}] ${s.title} — ${s.url}\n   ledger quotes: ${s.claim_ids.map(id => claimById(S, id)).filter(Boolean).map(c => `"${c.quote}"`).join(' / ')}`).join('\n')}

DRAFT:
${draft}`, REVIEW))
    lenses.forEach(([name, text]) => emit(`review${pass}-${name}`, `${header}\nLens: ${name}.\n${text}\n\nDRAFT:\n${draft}`, REVIEW))
    S.reviewNames = emitted.map(e => e.out.split('/').pop().replace('.json', '')); save(S)
    flushEmitted(`review pass ${pass}`)
  },
  'absorb-reviews'() {
    const S = load(), B = blocks(S), pass = Number(arg0 || 1)
    expectOuts(S.reviewNames)
    const reviews = S.reviewNames.map(readOut).filter(Boolean)
    const all = reviews.flatMap(r => (r.issues || []).map(i => ({ ...i, lens: r.lens })))
    S.allIssues = all; S.byLens = Object.fromEntries(reviews.map(r => [r.lens, (r.issues || []).length])); save(S)
    if (!all.length) { console.log('NONE issues'); return }
    emit(`rtriage-${pass}`, `You are the managing editor. ${all.length} issues were raised by reviewers on the current draft of a research report on "${S.plan.restated_question}". Merge duplicates (keep the best proposed fix), reject issues that are wrong, out of scope, or would shorten the report without cause (explain why), keep everything else. Keep any citation-audit issue marked unsupported/out_of_context as critical. Set pass_verdict="publishable" only if no critical or major issues remain accepted.
${B.STATUS_LEGEND}

ISSUES:
${all.map(i => `[${i.id}] (${i.lens}, ${i.severity}, section ${i.section_id}, needs_research=${i.needs_research})\n  text: "${i.offending_text}"\n  problem: ${i.problem}\n  fix: ${i.proposed_fix}${i.evidence_ids && i.evidence_ids.length ? `\n  evidence: ${i.evidence_ids.join(', ')}` : ''}${i.research_question ? `\n  research: ${i.research_question}` : ''}`).join('\n\n')}`, REVIEW_TRIAGE)
    console.log(`REVIEWS ${reviews.length}/${S.reviewNames.length}: ${all.length} issues (${JSON.stringify(S.byLens)})`)
    flushEmitted('review triage')
  },
  'absorb-rtriage'() {
    const S = load(), B = blocks(S), pass = Number(arg0 || 1)
    const t = readOut(`rtriage-${pass}`) || { accepted: [], rejected: [], pass_verdict: 'publishable' }
    const accepted = t.accepted || []
    const blocking = accepted.filter(i => i.severity === 'critical' || i.severity === 'major')
    S.reviewLog.push({ pass, raised: (S.allIssues || []).length, accepted: accepted.length, blocking: blocking.length, rejected: (t.rejected || []).length, by_lens: S.byLens || {}, verdict: t.pass_verdict })
    S.accepted = accepted; save(S)
    console.log(`RTRIAGE ${pass}: accepted ${accepted.length}, blocking ${blocking.length}, verdict ${t.pass_verdict}`)
    if (!accepted.length) { console.log('PUBLISHABLE'); return }
    const need = accepted.filter(i => i.needs_research && i.research_question)
    need.forEach((i, k) => emit(`gap-${pass}-${k}`, `Gap researcher for a report on "${S.plan.restated_question}". A reviewer (${i.lens || 'review'}) flagged: ${i.problem}\nResearch question: ${i.research_question}\n${B.TOOLS_NOTE}\n${B.SOURCE_RULES}\n${B.PLATFORM_RECIPES}\nOpen at least 6 sources; return claims with verbatim quotes, voices, numbers.`, FINDINGS))
    S.gapCount = need.length; save(S)
    flushEmitted(`gap research (then: absorb-gaps ${pass}, quotecheck rev${pass} cycle, rewrites ${pass})`)
    if (!need.length) console.log(`No gap research needed; run: rewrites ${pass}`)
  },
  'absorb-gaps'() {
    const S = load(), pass = Number(arg0 || 1)
    for (let k = 0; k < (S.gapCount || 0); k++) { const f = readOut(`gap-${pass}-${k}`); if (f) absorb(S, f, { kind: 'review-gap', ref: `RG${pass}-${k + 1}`, question: (S.accepted.filter(i => i.needs_research && i.research_question)[k] || {}).research_question || '', round: S.round, depth: 0 }) }
    save(S); console.log(`GAPS absorbed; pending claims ${S.claims.filter(c => c.status === 'pending').length}`)
  },
  rewrites() {
    const S = load(), B = blocks(S), pass = Number(arg0 || 1)
    const bySection = {}
    for (const i of S.accepted || []) (bySection[i.section_id] = bySection[i.section_id] || []).push(i)
    const newIds = S.claims.filter(c => c.origin.kind === 'review-gap' && c.status !== 'citation_failed').map(c => c.id)
    for (const [sid, issues] of Object.entries(bySection)) {
      const sec = S.sections.find(s => s.id === sid); if (!sec) { console.log(`SKIP issues for unknown section ${sid}`); continue }
      const spec = S.outline.sections.find(s => s.id === sid) || { id: sid, title: sec.title, claim_ids: [], must_cover: [], min_words: sec.word_count, target_words: sec.word_count }
      const slice = sliceFor(S, { ...spec, claim_ids: [...spec.claim_ids, ...newIds] })
      emit(`rewrite-${pass}-${sid}`, `You are rewriting section "${sec.title}" (id ${sid}) of a deep research report on "${S.plan.restated_question}" to resolve the accepted review issues below. Set id to "${sid}".
Rules: apply every fix; preserve all existing evidence, quotes and citations unless an issue says to remove them; keep the section at least as long as before (${sec.word_count} words) unless an issue explicitly calls for removal (then set length_reduction_justified=true); cite only with [S#] tokens from the ledger slice; do not introduce facts not in the slice; keep status and community labels. Do not include the H2 heading.
${B.STATUS_LEGEND}

ISSUES:
${issues.map(i => `- (${i.severity}) "${i.offending_text}" — ${i.problem} — FIX: ${i.proposed_fix}${i.evidence_ids && i.evidence_ids.length ? ` [evidence: ${i.evidence_ids.join(', ')}]` : ''}`).join('\n')}

CURRENT SECTION:
${sec.markdown}

${sliceText(slice)}`, SECTION)
    }
    S.rewriteIds = Object.keys(bySection); save(S)
    flushEmitted(`rewrites pass ${pass}`)
  },
  'absorb-rewrites'() {
    const S = load(), pass = Number(arg0 || 1)
    for (const sid of S.rewriteIds || []) {
      const r = readOut(`rewrite-${pass}-${sid}`); const idx = S.sections.findIndex(s => s.id === sid)
      if (!r || idx < 0) { console.log(`MISSING rewrite-${pass}-${sid}`); continue }
      const n = wc(r.markdown)
      if (n >= 0.9 * S.sections[idx].word_count || r.length_reduction_justified) S.sections[idx] = { ...S.sections[idx], markdown: r.markdown, word_count: n }
      else console.log(`REJECTED rewrite ${sid}: shrank ${S.sections[idx].word_count} -> ${n}`)
    }
    save(S)
    const last = S.reviewLog[S.reviewLog.length - 1]
    console.log(last && last.blocking === 0 && pass > 1 ? 'PUBLISHABLE' : (pass >= K(S).MAX_REVIEW_PASSES ? 'PUBLISHABLE (max passes)' : 'ANOTHER_PASS'))
  },
  assemble() {
    const S = load(), k = K(S)
    const finalSources = sourceList(S)
    const front = S.front
    const frontText = front ? `## Executive summary\n\n${front.executive_summary}\n\n## How to read this report\n\n${front.how_to_read}\n\n` : ''
    const bridges = new Map(front ? (front.bridges || []).map(b => [b.section_id, b.text]) : [])
    const body = S.sections.map(s => `## ${s.title}\n\n${bridges.get(s.id) ? `*${bridges.get(s.id)}*\n\n` : ''}${s.markdown}`).join('\n\n')
    const A = []
    A.push(`## Appendix A. Claim table\n\n| ID | Claim | Status | Source type | Date | Source | Origin |\n|---|---|---|---|---|---|---|\n${S.claims.map(c => `| ${c.id} | ${esc(c.claim)} | ${c.status} | ${c.source_type} | ${esc(c.published || '')} | [${c.sid}](${c.url}) | ${esc(c.origin.ref)} |`).join('\n')}`)
    A.push(`## Appendix B. Sources\n\n${finalSources.map(s => `${s.n}. **${esc(s.title)}** — ${s.platform}${s.published ? `, ${esc(s.published)}` : ''} — ${s.url} — ${s.source_type}; cited by ${s.claim_ids.length} claim(s)`).join('\n')}`)
    const vg = {}; for (const v of S.voices) (vg[v.platform || 'other'] = vg[v.platform || 'other'] || []).push(v)
    A.push(`## Appendix C. Community voices\n\n${Object.entries(vg).map(([p, vs]) => `### ${p}\n\n${vs.map(v => `> ${esc(v.quote)}\n> — ${esc(v.author)}, ${esc(v.date || 'undated')}, ${v.stance}${v.upvotes ? `, ${esc(v.upvotes)} votes` : ''}; credibility: ${esc(v.credibility)} — ${v.url}`).join('\n\n')}`).join('\n\n') || '_none recorded_'}`)
    A.push(`## Appendix D. Timeline\n\n${S.timeline.slice().sort((a, b) => String(a.date).localeCompare(String(b.date))).map(t => `- **${esc(t.date)}** — ${esc(t.event)}${t.url ? ` ([source](${t.url}))` : ''}`).join('\n') || '_none recorded_'}`)
    A.push(`## Appendix E. Numbers\n\n| What | Value | Who | Date | Challenged | Source |\n|---|---|---|---|---|---|\n${S.numbers.map(n => `| ${esc(n.what)} | ${esc(n.value)} | ${esc(n.who || '')} | ${esc(n.date || '')} | ${n.challenged ? 'yes' : ''} | ${n.url} |`).join('\n')}`)
    if (front) A.push(`## Appendix F. Glossary\n\n${front.glossary}`)
    A.push(`## Appendix G. Entity dossiers\n\n${S.dossiers.map(d => `### ${d.name} (${d.entity_type}, swarm ${d.swarm_id}, depth ${d.depth})\n\n${d.what_it_is}\n\n**Consensus:**${(d.consensus_claims || []).map(x => `\n- ${x}`).join('')}\n\n**Dissent:**${(d.dissent || []).map(x => `\n- ${x}`).join('') || ' none recorded'}\n\n**Primary sources:** ${(d.primary_sources || []).join('; ') || 'none'}\n\n**Credibility:** ${d.credibility_assessment}\n\n**Relation to the question:** ${d.relation_to_question}\n\n**Open questions:**${(d.open_questions || []).map(x => `\n- ${x}`).join('') || ' none'}`).join('\n\n') || '_no swarms were run_'}`)
    A.push(`## Appendix H. Dissent register\n\n### Contradictions noted by researchers\n${S.entries.flatMap(e => (e.contradictions || []).map(c => `- (${e.id}) ${esc(c)}`)).join('\n') || '- none'}\n\n### Contested, refuted and outdated claims\n${S.claims.filter(c => ['contested', 'refuted', 'outdated'].includes(c.status)).map(c => `- **${c.id}** [${c.status}] ${esc(c.claim)} — ${c.notes.map(esc).join(' / ')}`).join('\n') || '- none'}\n\n### Claims whose citation failed verification\n${S.claims.filter(c => c.status === 'citation_failed').map(c => `- **${c.id}** ${esc(c.claim)} — ${c.url} — ${c.notes.map(esc).join(' / ')}`).join('\n') || '- none'}`)
    A.push(`## Appendix I. Unexplored leads\n\n${S.parked.map(l => `- **${esc(l.name)}** (${l.entity_type}, score ${l.prescore}, round ${l.round}) — ${esc(l.lead)} — parked: ${esc(l.why_parked)}${l.canonical_url ? ` — ${l.canonical_url}` : ''}`).join('\n') || '- none'}\n\n### Unanswered items\n${S.entries.flatMap(e => (e.unanswered || []).map(u => `- (${e.id}) ${esc(u)}`)).join('\n') || '- none'}\n\n### Proposed but unresearched sub-questions\n${(S.unresearched || []).map(u => `- ${esc(u)}`).join('\n') || '- none'}`)
    const last = S.reviewLog[S.reviewLog.length - 1]
    A.push(`## Appendix J. Methodology and review log\n\n- Rounds: ${S.round} (min ${k.MIN_ROUNDS}, max ${k.MAX_ROUNDS}); depth mode: ${S.MAX ? 'max' : 'standard'}\n- Sub-questions researched: ${S.entries.filter(e => e.kind === 'subquestion').length}, each by three researchers (primary, community, contrarian) plus second passes where thin\n- Deep-dive swarms: ${Object.keys(S.swarmed).length} (${Object.values(S.swarmed).map(v => `${v.name} [${v.entity_type}, depth ${v.depth}, ${v.agents} agents]`).join('; ') || 'none'})\n- Follow-ups: ${S.entries.filter(e => e.kind === 'followup').length}\n- Claims: ${S.claims.length} total; ${statLine(S)}\n- Sources: ${Object.keys(S.sources).length}; community voices: ${S.voices.length}; numbers: ${S.numbers.length}; timeline entries: ${S.timeline.length}\n- Verification: every claim quote-checked against its page; key and community claims judged by ${k.SKEPTICS}-skeptic panels with an adjudicator on split votes; other claims source-checked only\n- Review passes: ${S.reviewLog.length}\n\n| Pass | Issues raised | Accepted | Blocking | Rejected | By lens |\n|---|---|---|---|---|---|\n${S.reviewLog.map(r => `| ${r.pass} | ${r.raised} | ${r.accepted} | ${r.blocking} | ${r.rejected} | ${esc(Object.entries(r.by_lens).map(([k2, v]) => `${k2} ${v}`).join(', '))} |`).join('\n')}\n${last && last.blocking ? `\n**Known limitations:** ${last.blocking} blocking review issue(s) remained when the review budget was exhausted.` : ''}`)
    const byToken = new Map(finalSources.map(s => [s.id, s]))
    const resolve = text => text.replace(/\[(S\d+)\]/g, (m, t) => { const s = byToken.get(t); return s ? `[${s.n}](${s.url})` : m })
    const toc = `## Contents\n\n${['Executive summary', 'How to read this report', ...S.sections.map(s => s.title), ...A.map(a => a.split('\n')[0].replace(/^## /, ''))].map((t, i) => `${i + 1}. ${t}`).join('\n')}`
    const report = resolve(`# ${S.outline.title}\n\n_Research completed ${S.args.today}. ${S.claims.length} claims from ${Object.keys(S.sources).length} sources; ${Object.keys(S.swarmed).length} deep-dive swarms; ${S.reviewLog.length} review passes._\n\n${toc}\n\n${frontText}${body}\n\n# Appendices\n\n${A.join('\n\n')}`)
    writeFileSync(join(RUN, 'report.md'), report)
    const wordsBody = S.sections.reduce((n, s) => n + s.word_count, 0) + (front ? wc(front.executive_summary) + wc(front.how_to_read) : 0)
    console.log(JSON.stringify({ report: join(RUN, 'report.md'), words_body: wordsBody, words_total: wc(report), sections: S.sections.length, rounds: S.round, swarms: Object.values(S.swarmed).map(v => v.name), claims: { total: S.claims.length, ...stats(S) }, sources: Object.keys(S.sources).length, voices: S.voices.length, review_passes: S.reviewLog.length, blocking_remaining: last ? last.blocking : 0, parked_leads: S.parked.length, unresearched: S.unresearched || [] }, null, 1))
  },
  status() {
    const S = load()
    console.log(JSON.stringify({ round: S.round, queue: S.queue.length, claims: S.claims.length, stats: stats(S), sources: Object.keys(S.sources).length, voices: S.voices.length, swarms: Object.values(S.swarmed).map(v => v.name), dossiers: S.dossiers.length, parked: S.parked.length, sections: S.sections.length, reviewLog: S.reviewLog }, null, 1))
  },
}

// ---------------------------------------------------------------- writing helpers
const draftText = secs => secs.map(s => `## ${s.title} {#${s.id}}\n\n${s.markdown}`).join('\n\n')
function sliceFor(S, spec) {
  const ids = new Set(spec.claim_ids || [])
  const cs = usable(S).filter(c => ids.has(c.id))
  const urls = new Set(cs.map(c => normUrl(c.url)))
  const ds = S.dossiers.filter(d => (spec.dossier_names || []).includes(d.name))
  const names = ds.map(d => d.name)
  const tag = `${spec.id} ${spec.title}`
  const vs = S.voices.filter(v => urls.has(normUrl(v.url)) || names.includes(v.entity) || /practitioner|voice|community/i.test(tag)).slice(0, 60)
  const ns = S.numbers.filter(n => urls.has(normUrl(n.url)) || /quant/i.test(tag)).slice(0, 120)
  const ts = /landscape|timeline|trail|history/i.test(tag) ? S.timeline.slice(0, 120) : S.timeline.filter(t => urls.has(normUrl(t.url))).slice(0, 40)
  return { cs, ds, vs, ns, ts }
}
const sliceText = ({ cs, ds, vs, ns, ts }) => `LEDGER SLICE (cite with [S#] tokens exactly as given, e.g. [${cs[0] ? cs[0].sid : 'S1'}]; claim ids as [C####]):
${cs.map(claimFull).join('\n')}

DOSSIERS:
${ds.map(d => `### ${d.name} (${d.entity_type})\n${d.what_it_is}\nConsensus: ${(d.consensus_claims || []).join('; ')}\nDissent: ${(d.dissent || []).join('; ')}\nPrimary sources: ${(d.primary_sources || []).join('; ')}\nCredibility: ${d.credibility_assessment}\nRelation to question: ${d.relation_to_question}\nOpen: ${(d.open_questions || []).join('; ')}`).join('\n\n') || 'none'}

VOICES (verbatim community quotes; cite the [S#] token of a claim from the same URL where one exists, else give platform/author/date inline):
${vs.map(v => `- "${v.quote}" — ${v.author}, ${v.platform}, ${v.date || 'undated'}, ${v.stance}, credibility: ${v.credibility}${v.upvotes ? `, votes ${v.upvotes}` : ''} — ${v.url}`).join('\n') || 'none'}

NUMBERS:
${ns.map(n => `- ${n.what}: ${n.value} (${n.who || 'unattributed'}, ${n.date || 'undated'}${n.challenged ? ', CHALLENGED' : ''}) — ${n.url}`).join('\n') || 'none'}

TIMELINE:
${ts.map(t => `- ${t.date}: ${t.event}${t.url ? ` — ${t.url}` : ''}`).join('\n') || 'none'}`

function writePrompts(S, only, prev) {
  const B = blocks(S)
  const specs = only ? [only] : S.outline.sections
  for (const spec of specs) {
    const slice = sliceFor(S, spec)
    const others = S.outline.sections.filter(s => s.id !== spec.id).map(s => `${s.id}: ${s.title} — ${s.purpose}`).join(' | ')
    emit(prev ? `expand-${spec.id}` : `write-${spec.id}`, `You are writing ONE section of a very long, exhaustive research report. Other agents write the other sections; do not summarise the whole report or write a report introduction.
REPORT QUESTION: "${S.plan.restated_question}"
${B.OBJECTIVE_NOTE}
${B.EXAMPLES.length ? `The user's example(s) (${B.EXAMPLES.join('; ')}) were illustrations; write at the category level and use them only as data points.` : ''}
Today: ${S.args.today}.

YOUR SECTION: ${spec.title} (id ${spec.id}) — ${spec.purpose}
Set id to "${spec.id}" and title to "${spec.title}".
Must cover: ${(spec.must_cover || []).join('; ')}
Tables required: ${(spec.tables || []).join('; ') || 'any comparison of 4+ items'}
LENGTH: at least ${spec.min_words} words, target ${spec.target_words}. Depth is the point: a reader should finish knowing everything the team learned on this theme, including nuances, numbers, dissent and who said what. Do not compress; expand. Every relevant claim in your slice should appear.
Other sections (do not duplicate them): ${others}

Rules:
- Use ONLY the ledger slice, dossiers, voices, numbers and timeline below. No facts from memory.
- Cite every factual sentence with its source token [S#] (the exact token given for that source). You may add the claim id [C####]. Never write URLs or footnote numbers yourself; the script resolves tokens.
- ${B.STATUS_LEGEND} Build on confirmed and source_checked claims (say "source-checked" where a reader should know it is single-sourced); label contested ones "(contested: ...)"; state refuted/outdated ones only as debunked/outdated; label community evidence with its spread, e.g. "(community: r/x, 2023, ~12 users)".
- Quote community voices verbatim in block quotes with username, platform, date and the [S#] token where available; prefer firsthand experience and sharp dissent.
- Subheadings (###) every 300-500 words; tables for any comparison of 4+ items.
- Direct, specific register. No filler, no "it is important to note".
- Do not include the section's H2 heading; start with the body.
- Return an honest word_count.
${prev ? `\nYOUR PREVIOUS DRAFT was ${wc(prev.markdown)} words; the minimum is ${spec.min_words}. Expand it using the claims below that it did not use: ${slice.cs.filter(c => !(prev.claim_ids_used || []).includes(c.id)).map(c => c.id).join(', ') || '(use more detail, voices, numbers and tables)'}.\nPREVIOUS DRAFT:\n${prev.markdown}\n` : ''}
${sliceText(slice)}`, SECTION)
  }
  if (!only) flushEmitted('section writers')
}

if (!commands[cmd]) { console.error(`unknown command ${cmd}; commands: ${Object.keys(commands).join(', ')}`); process.exit(1) }
commands[cmd]()
