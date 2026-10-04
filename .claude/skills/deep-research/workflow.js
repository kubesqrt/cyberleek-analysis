export const meta = {
  name: 'deep-research',
  description: 'Exhaustive multi-agent research: plan, researcher trios, lead triage, deep-dive swarms, full verification, director loop, parallel section writers, multi-pass review',
  whenToUse: 'In-depth research on any question or objective where coverage, forum evidence and verified citations matter',
  phases: [
    { title: 'Plan', detail: 'orienting scouts, then decomposition into sub-questions' },
    { title: 'Research', detail: 'three researchers per sub-question: primary, community, contrarian' },
    { title: 'Swarm', detail: 'lead triage, then 5-12 agent swarms that exhaust each promising entity' },
    { title: 'Verify', detail: 'quote-check every claim, then skeptic panels and an adjudicator' },
    { title: 'Direct', detail: 'director and stop-auditor decide what to research next' },
    { title: 'Write', detail: 'outline, one writer per section, appendices, stitcher' },
    { title: 'Review', detail: 'ten reviewer lenses, triage, targeted rewrites, repeat' },
  ],
}

// args: { question, objective?, context?, examples?: string[], today, depth?: 'standard'|'max', min_words?: number }
const Q = typeof args === 'string' ? { question: args } : (args || {})
if (!Q.question) throw new Error('deep-research: pass args.question')
if (!Q.today) throw new Error('deep-research: pass args.today (YYYY-MM-DD); scripts cannot read the clock')
const MAX = Q.depth === 'max'
const TODAY = Q.today
const OBJECTIVE = Q.objective || ''
const EXAMPLES = Array.isArray(Q.examples) ? Q.examples.filter(Boolean) : []

// ---- knobs ----
const MIN_ROUNDS = MAX ? 3 : 2
const MAX_ROUNDS = MAX ? 6 : 4
const SKEPTICS = 3                           // odd; per chunk of key claims
const CHUNK = 12                             // claims per quote-check agent
const JUDGE_CHUNK = 10                       // key claims per skeptic agent
const SWARMS_PER_ROUND = MAX ? 12 : 6
const MAX_SWARMS = MAX ? 40 : 18
const MAX_DEPTH = MAX ? 3 : 2
const MIN_SOURCES = MAX ? 12 : 8
const MIN_SEARCHES = MAX ? 15 : 10
const MIN_BODY_WORDS = Q.min_words || (MAX ? 16000 : 9000)
const MAX_REVIEW_PASSES = MAX ? 5 : 3
const BUDGET = 950                           // lifetime agent cap is 1000

// ---- budget governor + spawn with one retry ----
let used = 0
const downgrades = []
const governor = {
  tier: () => used < 0.75 * BUDGET ? 'full' : used < 0.92 * BUDGET ? 'reduced' : 'minimal',
  skeptics: () => ({ full: SKEPTICS, reduced: 1, minimal: 0 })[governor.tier()],
  allowsSwarm: () => governor.tier() === 'full',
  allowsFollowup: () => governor.tier() !== 'minimal',
  reviewPasses: () => ({ full: MAX_REVIEW_PASSES, reduced: 2, minimal: 1 })[governor.tier()],
}
let lastTier = 'full'
const checkTier = () => { const t = governor.tier(); if (t !== lastTier) { downgrades.push(`agents=${used}: ${lastTier} -> ${t}`); log(`Budget governor: ${lastTier} -> ${t} (${used} agents used)`); lastTier = t } }
async function spawn(prompt, opts) {
  if (used >= BUDGET) return null
  used++; checkTier()
  let r = null
  try { r = await agent(prompt, opts) } catch (e) { r = null }
  if (r == null && used < BUDGET) {
    used++
    try { r = await agent(prompt + '\n\n(Your previous attempt returned no valid result. Return valid output matching the schema.)', { ...opts, label: (opts.label || 'agent') + ':retry' }) } catch (e) { r = null }
  }
  return r
}
const wc = s => (s || '').trim().split(/\s+/).filter(Boolean).length
const chunk = (arr, n) => { const out = []; for (let i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n)); return out }
const normUrl = u => (u || '').toLowerCase().replace(/^https?:\/\/(www\.|old\.|new\.|m\.)?/, '').replace(/[?#].*$/, '').replace(/\/+$/, '')
const host = u => { const m = (u || '').match(/^https?:\/\/([^/]+)/i); return m ? m[1].toLowerCase().replace(/^www\./, '') : '' }

// ---- shared prompt blocks ----
const OBJECTIVE_NOTE = OBJECTIVE ? `USER'S OBJECTIVE (what they want to achieve with this research): ${OBJECTIVE}
Favour findings that are actionable for this objective: options, approaches, tools, pitfalls and tips that real people report.` : ''

const EXAMPLES_NOTE = EXAMPLES.length ? `ILLUSTRATIVE EXAMPLES (given by the user to show what they mean; they are NOT the research target):
${EXAMPLES.map(e => `- ${e}`).join('\n')}
Research the general category these examples belong to. An example may appear as one data point among many, never as the focus.` : ''

const TOOLS_NOTE = `Tools: first run ToolSearch with query "select:WebSearch,WebFetch" to load web tools.
Use WebSearch mode "extended" for anything niche, recent, numeric or contested; "standard" for quick lookups.
Open and read the actual pages with WebFetch. Never cite a page from its search snippet or from another site's summary of it.
Today's date: ${TODAY}.`

const SOURCE_RULES = `Source rules:
- Prefer primary sources: official docs, filings, datasets, papers, statutes, standards, the original announcement, the author's own words.
- SEO blogs, content farms, AI-generated summaries and undated pages are "weak"; use them only to find primary sources.
- Forum/community posts are source_type "community": experience reports and leads, not established fact. They are strong only when several independent users report the same thing.
- Record the publication date and title of every source. Flag anything that may be outdated.
- Every claim needs a URL plus a short verbatim quote that supports it. No quote, no claim.
- Separate fact from opinion/forecast. Note when sources disagree instead of picking one silently.
- If you cannot find something, say so. Never fill gaps from memory.`

const LEAD_RULES = `Leads: every tool, person, organisation, document/study, thread, community, term or event you meet that deserves its own investigation goes in leads[], with entity_type, name, canonical_url, how many distinct sources mentioned it, and the specific questions you could not answer about it. Mark relevance "central" if it could change the answer or a recommendation. Follow each lead one hop so you can describe it, then hand it over: dedicated swarms do the deep chasing.`

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
STACK EXCHANGE: https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=votes&q=<q>&site=<site>&filter=withbody&pagesize=100; answers /2.3/questions/<id>/answers?order=desc&sort=votes&site=<site>&filter=withbody; comments (where corrections live) /2.3/answers/<id>/comments?site=<site>&filter=withbody. Distinguish accepted vs highest-voted vs most recent; a 2023 comment saying "this no longer works" on a 2014 answer is a key finding.
GITHUB: issues sorted by reactions https://github.com/<o>/<r>/issues?q=<q>+is%3Aissue+sort%3Areactions-%2B1-desc (also is:closed, wontfix/not-planned labels); REST https://api.github.com/repos/<o>/<r>/issues/<n>/comments?per_page=100; discussions ?discussions_q=; releases/CHANGELOG for dating; author_association marks maintainers. Use GitHub MCP tools if available in your tool list.
DISCOURSE forums: https://<forum>/t/<slug>/<id>.json gives posts_count and all post ids in post_stream.stream; fetch the rest via /t/<id>/posts.json?post_ids[]=<id>&post_ids[]=<id> (20 per call) or ?print=true. Search /search.json?q=<q> order:latest (modifiers in:title, after:, category:, status:solved, order:likes). Users /u/<name>.json (trust_level, title).
YOUTUBE: watch page meta for date/channel; transcripts and comments via Invidious instances (https://api.invidious.io/instances.json; /api/v1/captions/<id>, /api/v1/comments/<id>?sort_by=top) or Piped (pipedapi.kavin.rocks/streams/<id>, /comments/<id>). Try at least two mirrors; never claim a video said something without a transcript quote.
OTHER: phpBB viewtopic.php?t=<id>&start=<n>; XenForo /threads/<slug>.<id>/page-N; Lemmy /api/v3/comment/list?post_id=<id>&max_depth=8; Discord archives via linen.dev and answeroverflow.com; Telegram https://t.me/s/<channel>?q=<term>; X/Twitter is unreliable (nitter/Wayback, else say unverifiable). Review sites: read 1-star and 5-star sorted by recent; watch for review bursts. Paywalled: Wayback, archive.ph, r.jina.ai, AMP, arXiv/SSRN/author pages.
Record which mirror or fallback you used in coverage_note or access_note.`

// ---- schemas ----
const SUBQ_ITEM = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    question: { type: 'string' },
    why: { type: 'string' },
    search_angles: { type: 'array', items: { type: 'string' } },
  },
  required: ['id', 'question', 'search_angles'],
}

const PLAN = {
  type: 'object',
  properties: {
    restated_question: { type: 'string' },
    field: { type: 'string', description: 'the domain/field this question belongs to, for expert reviewers' },
    assumptions: { type: 'array', items: { type: 'string' } },
    subquestions: { type: 'array', items: SUBQ_ITEM },
  },
  required: ['restated_question', 'field', 'subquestions'],
}

const ORIENT = {
  type: 'object',
  properties: {
    landscape: { type: 'string', description: '300-600 words: what this topic looks like from your angle' },
    insider_terms: { type: 'array', items: { type: 'string' } },
    key_entities: { type: 'array', items: { type: 'string' } },
    where_the_data_lives: { type: 'array', items: { type: 'string' } },
    communities: { type: 'array', items: { type: 'string' }, description: 'forums/subreddits/communities where practitioners discuss this' },
  },
  required: ['landscape', 'insider_terms', 'key_entities', 'communities'],
}

const CLAIM = {
  type: 'object',
  properties: {
    claim: { type: 'string' },
    url: { type: 'string' },
    title: { type: 'string', description: 'page/document title' },
    quote: { type: 'string', description: 'verbatim, <= 60 words' },
    source_type: { type: 'string', enum: ['primary', 'secondary', 'community', 'weak'] },
    published: { type: 'string' },
    author: { type: 'string' },
    key: { type: 'boolean', description: 'true if the final answer or a recommendation depends on this claim' },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
    access_note: { type: 'string', description: 'e.g. "via Wayback 2024-03-02", if a mirror was used' },
  },
  required: ['claim', 'url', 'title', 'quote', 'source_type', 'key', 'confidence'],
}

const LEAD = {
  type: 'object',
  properties: {
    lead: { type: 'string', description: 'one sentence: what this is and why it looked promising' },
    entity_type: { type: 'string', enum: ['thread', 'community', 'tool', 'person', 'org', 'term', 'document', 'event', 'dataset', 'other'] },
    name: { type: 'string' },
    canonical_url: { type: 'string' },
    found_in: { type: 'array', items: { type: 'string' } },
    mention_count: { type: 'integer' },
    size_hint: { type: 'string' },
    relevance: { type: 'string', enum: ['central', 'supporting', 'tangential'] },
    contested: { type: 'boolean' },
    hops_taken: { type: 'integer' },
    what_is_unknown: { type: 'string' },
  },
  required: ['lead', 'entity_type', 'name', 'relevance', 'mention_count', 'hops_taken', 'what_is_unknown'],
}

const VOICE = {
  type: 'object',
  properties: {
    quote: { type: 'string', description: 'verbatim, <= 80 words' },
    author: { type: 'string' }, platform: { type: 'string' }, url: { type: 'string' }, date: { type: 'string' },
    stance: { type: 'string', enum: ['supports_consensus', 'dissents', 'nuance', 'firsthand_experience', 'expert'] },
    credibility: { type: 'string' },
    upvotes: { type: 'string' },
  },
  required: ['quote', 'author', 'platform', 'url', 'stance', 'credibility'],
}

const FINDINGS = {
  type: 'object',
  properties: {
    summary: { type: 'string', description: '200-500 words' },
    claims: { type: 'array', items: CLAIM },
    voices: { type: 'array', items: VOICE },
    numbers: { type: 'array', items: { type: 'object', properties: { what: { type: 'string' }, value: { type: 'string' }, who: { type: 'string' }, url: { type: 'string' }, date: { type: 'string' }, challenged: { type: 'boolean' } }, required: ['what', 'value', 'url'] } },
    timeline: { type: 'array', items: { type: 'object', properties: { date: { type: 'string' }, event: { type: 'string' }, url: { type: 'string' } }, required: ['date', 'event'] } },
    contradictions: { type: 'array', items: { type: 'string' } },
    unanswered: { type: 'array', items: { type: 'string' } },
    leads: { type: 'array', items: LEAD },
    sources_read: { type: 'array', items: { type: 'string' }, description: 'every URL actually opened' },
    searches_run: { type: 'array', items: { type: 'string' } },
    coverage_note: { type: 'string' },
  },
  required: ['summary', 'claims', 'voices', 'numbers', 'contradictions', 'unanswered', 'leads', 'sources_read', 'searches_run'],
}

const SWARM_FINDINGS = {
  ...FINDINGS,
  properties: {
    ...FINDINGS.properties,
    angle: { type: 'string' },
    recurring_claims: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, supporters: { type: 'integer' }, dissenters: { type: 'integer' }, strongest_evidence_url: { type: 'string' }, strongest_dissent_quote: { type: 'string' } }, required: ['claim', 'supporters', 'dissenters'] } },
    answers: { type: 'array', items: { type: 'object', properties: { question: { type: 'string' }, answer: { type: 'string' } }, required: ['question', 'answer'] } },
  },
  required: [...FINDINGS.required, 'angle', 'recurring_claims', 'answers', 'coverage_note'],
}

const DOSSIER = {
  type: 'object',
  properties: {
    name: { type: 'string' }, entity_type: { type: 'string' },
    one_paragraph: { type: 'string' },
    what_it_is: { type: 'string', description: '400-1000 words synthesising every angle' },
    consensus_claims: { type: 'array', items: { type: 'string' } },
    dissent: { type: 'array', items: { type: 'string' } },
    primary_sources: { type: 'array', items: { type: 'string' } },
    credibility_assessment: { type: 'string' },
    relation_to_question: { type: 'string' },
    open_questions: { type: 'array', items: { type: 'string' } },
    recommended_followups: { type: 'array', items: LEAD },
  },
  required: ['name', 'entity_type', 'one_paragraph', 'what_it_is', 'consensus_claims', 'dissent', 'credibility_assessment', 'relation_to_question', 'open_questions', 'recommended_followups'],
}

const TRIAGE = {
  type: 'object',
  properties: {
    decisions: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string' },
      tier: { type: 'string', enum: ['swarm', 'followup', 'park'] },
      why: { type: 'string' },
      questions_to_answer: { type: 'array', items: { type: 'string' } },
    }, required: ['key', 'tier', 'why', 'questions_to_answer'] } },
  },
  required: ['decisions'],
}

const QUOTE_CHECKS = {
  type: 'object',
  properties: {
    checks: { type: 'array', items: { type: 'object', properties: {
      claim_id: { type: 'string' },
      reachable: { type: 'boolean' },
      archive_url_used: { type: 'string' },
      quote_found: { type: 'string', enum: ['verbatim', 'near_verbatim', 'paraphrase_only', 'not_found'] },
      supports_claim: { type: 'string', enum: ['yes', 'partially', 'no', 'out_of_context'] },
      page_date: { type: 'string' },
      note: { type: 'string' },
    }, required: ['claim_id', 'reachable', 'quote_found', 'supports_claim'] } },
  },
  required: ['checks'],
}

const VERDICTS = {
  type: 'object',
  properties: {
    verdicts: { type: 'array', items: { type: 'object', properties: {
      claim_id: { type: 'string' },
      status: { type: 'string', enum: ['confirmed', 'refuted', 'unclear', 'outdated'] },
      evidence_url: { type: 'string' },
      note: { type: 'string' },
    }, required: ['claim_id', 'status', 'note'] } },
  },
  required: ['verdicts'],
}

const GAPS = {
  type: 'object',
  properties: {
    done: { type: 'boolean' },
    coverage_assessment: { type: 'object', properties: {
      breadth: { type: 'string', enum: ['thin', 'adequate', 'strong'] },
      depth: { type: 'string', enum: ['thin', 'adequate', 'strong'] },
      counter_evidence: { type: 'string', enum: ['thin', 'adequate', 'strong'] },
      recency: { type: 'string', enum: ['thin', 'adequate', 'strong'] },
      quantitative: { type: 'string', enum: ['thin', 'adequate', 'strong'] },
      community: { type: 'string', enum: ['thin', 'adequate', 'strong'] },
    }, required: ['breadth', 'depth', 'counter_evidence', 'recency', 'quantitative', 'community'] },
    reasoning: { type: 'string' },
    new_subquestions: { type: 'array', items: SUBQ_ITEM },
  },
  required: ['done', 'coverage_assessment', 'reasoning', 'new_subquestions'],
}

const OUTLINE = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    sections: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, title: { type: 'string' }, purpose: { type: 'string' },
      claim_ids: { type: 'array', items: { type: 'string' } },
      dossier_names: { type: 'array', items: { type: 'string' } },
      voice_filter: { type: 'string' },
      min_words: { type: 'integer' }, target_words: { type: 'integer' },
      must_cover: { type: 'array', items: { type: 'string' } },
      tables: { type: 'array', items: { type: 'string' } },
    }, required: ['id', 'title', 'purpose', 'claim_ids', 'min_words', 'target_words', 'must_cover'] } },
  },
  required: ['title', 'sections'],
}

const SECTION = {
  type: 'object',
  properties: {
    id: { type: 'string' }, title: { type: 'string' },
    markdown: { type: 'string', description: 'the full section in markdown, citing only [S##] and [C####] tokens; do not include the H2 heading' },
    word_count: { type: 'integer' },
    claim_ids_used: { type: 'array', items: { type: 'string' } },
    length_reduction_justified: { type: 'boolean' },
  },
  required: ['id', 'title', 'markdown', 'word_count', 'claim_ids_used'],
}

const FRONT = {
  type: 'object',
  properties: {
    executive_summary: { type: 'string', description: '600-1000 words markdown' },
    how_to_read: { type: 'string', description: '300+ words markdown' },
    bridges: { type: 'array', items: { type: 'object', properties: { section_id: { type: 'string' }, text: { type: 'string' } }, required: ['section_id', 'text'] }, description: '2-3 sentence bridge to open each section' },
    glossary: { type: 'string', description: 'markdown: every insider term, acronym, tool and named entity, 1-3 sentences each, with [S##] where a source defines it' },
  },
  required: ['executive_summary', 'how_to_read', 'bridges', 'glossary'],
}

const ISSUE = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    severity: { type: 'string', enum: ['critical', 'major', 'minor', 'nit'] },
    section_id: { type: 'string' },
    offending_text: { type: 'string', description: 'verbatim excerpt <= 60 words' },
    problem: { type: 'string' },
    proposed_fix: { type: 'string' },
    evidence_ids: { type: 'array', items: { type: 'string' } },
    needs_research: { type: 'boolean' },
    research_question: { type: 'string' },
    touches_conclusions: { type: 'boolean' },
  },
  required: ['id', 'severity', 'section_id', 'offending_text', 'problem', 'proposed_fix', 'needs_research', 'touches_conclusions'],
}

const REVIEW = {
  type: 'object',
  properties: { lens: { type: 'string' }, overall: { type: 'string' }, issues: { type: 'array', items: ISSUE } },
  required: ['lens', 'overall', 'issues'],
}

const REVIEW_TRIAGE = {
  type: 'object',
  properties: {
    accepted: { type: 'array', items: ISSUE },
    rejected: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, why: { type: 'string' } }, required: ['id', 'why'] } },
    pass_verdict: { type: 'string', enum: ['publishable', 'needs_another_pass'] },
  },
  required: ['accepted', 'rejected', 'pass_verdict'],
}

// ---- ledger ----
const claims = []                  // {id, sid, ...CLAIM, origin:{kind,ref,round}, status, notes:[]}
const claimById = new Map()
const sources = new Map()          // normUrl -> {id:'S12', n, url, title, platform, source_type, claim_ids:[]}
const entries = []                 // {id, question, kind, round, summary, claim_ids, unanswered, contradictions, coverage, leads, depth}
const voices = [], numbers = [], timeline = []
const dossiers = []
const parked = []
const swarmed = new Map()          // entityKey -> {name, entity_type, depth, round, agents}
const swarmedNames = new Set()     // lowercase names, so the same entity under another URL is not swarmed twice
const seenSubq = []
const reviewLog = []
let claimCounter = 0, sourceCounter = 0

function addSource(c) {
  const k = normUrl(c.url)
  if (!k) return null
  if (!sources.has(k)) { sourceCounter++; sources.set(k, { id: `S${sourceCounter}`, n: sourceCounter, url: c.url, title: c.title || c.url, platform: host(c.url), source_type: c.source_type, published: c.published || '', claim_ids: [] }) }
  return sources.get(k)
}

function absorb(found, origin) {
  if (!found || !Array.isArray(found.claims)) return null
  const ids = []
  for (const c of found.claims) {
    if (!c.url || !c.quote) continue
    const s = addSource(c); if (!s) continue
    claimCounter++
    const id = `C${String(claimCounter).padStart(4, '0')}`
    const rec = { ...c, id, sid: s.id, origin, status: 'pending', notes: [] }
    claims.push(rec); claimById.set(id, rec); s.claim_ids.push(id); ids.push(id)
  }
  for (const v of found.voices || []) voices.push({ ...v, origin: origin.ref, entity: origin.entity || '' })
  for (const n of found.numbers || []) numbers.push({ ...n, origin: origin.ref })
  for (const t of found.timeline || []) timeline.push({ ...t, origin: origin.ref })
  const e = { id: origin.ref, question: origin.question, kind: origin.kind, round: origin.round, depth: origin.depth || 0, entity: origin.entity || '', summary: found.summary || '', claim_ids: ids, unanswered: found.unanswered || [], contradictions: found.contradictions || [], coverage: found.coverage_note || '', leads: found.leads || [], recurring: found.recurring_claims || [], answers: found.answers || [] }
  entries.push(e)
  return e
}

const claimLine = c => `${c.id} [${c.status}] [${c.source_type}${c.published ? ', ' + c.published : ''}] ${c.claim} — ${c.sid}`
const claimFull = c => `${c.id} [${c.status}] [${c.source_type}${c.published ? ', ' + c.published : ''}] ${c.claim}
    source ${c.sid}: ${c.title} — ${c.url}${c.access_note ? ` (${c.access_note})` : ''}
    quote: "${c.quote}"${c.notes.length ? `\n    verification: ${c.notes.join(' | ')}` : ''}`
const stats = () => { const s = {}; for (const c of claims) s[c.status] = (s[c.status] || 0) + 1; return s }

// =====================================================================
// PLAN
// =====================================================================
phase('Plan')
const scoutAngles = [
  'the official/primary-source view: who the authorities are, what the canonical documents and datasets are, how the field defines its terms',
  'the practitioner/community view: which forums, subreddits, Discourse boards, GitHub repos, Discord archives and YouTube channels practitioners use, and the insider vocabulary they use',
  'the contrarian/critical view: who disputes the mainstream take, what the known failure modes and controversies are, what adjacent fields say',
]
const scouts = (await parallel(scoutAngles.map((a, i) => () => spawn(`You are an orienting scout for a deep research project.
QUESTION: ${Q.question}
${Q.context ? `CONTEXT FROM THE USER: ${Q.context}` : ''}
${OBJECTIVE_NOTE}
${EXAMPLES_NOTE}
Your angle: ${a}.
${TOOLS_NOTE}
Run at least 8 varied searches and open at least 8 pages. Map the landscape from your angle so the planner can decompose the question well. Do not try to answer the question.`, { phase: 'Plan', label: `scout:${i + 1}`, schema: ORIENT })))).filter(Boolean)

const plan = await spawn(`You are planning a deep research project.

QUESTION: ${Q.question}
${Q.context ? `CONTEXT FROM THE USER: ${Q.context}` : ''}
${OBJECTIVE_NOTE}
${EXAMPLES_NOTE}

Scout reports:
${scouts.map((s, i) => `--- Scout ${i + 1} ---\n${s.landscape}\nInsider terms: ${s.insider_terms.join(', ')}\nKey entities: ${s.key_entities.join(', ')}\nCommunities: ${s.communities.join(', ')}\nData lives at: ${(s.where_the_data_lives || []).join(', ')}`).join('\n\n')}

${TOOLS_NOTE}
${EXAMPLES.length ? `
Anti-anchoring rules:
- At most ONE sub-question may be about the given example(s) specifically.
- Include a sub-question that maps the whole landscape (enumerate the other members of the category).
- Include a sub-question on how instances differ and on counter-examples that break the pattern.
- Search angles must use category-level terms, not only the example's name.
` : ''}
Break the question into ${MAX ? '10-14' : '8-10'} sub-questions that together fully answer it with minimal overlap.
Include sub-questions for: definitions/scope; the core facts; quantitative data; the strongest counter-evidence or opposing view; recent developments; practical implications; at least ${MAX ? 2 : 1} on what practitioners say in forums and communities (experiences, complaints, workarounds, hidden alternatives); one deliberately lateral angle (adjacent field, unconventional framing).${OBJECTIVE ? '\nSince the user has an objective, include a sub-question that surveys the realistic options/approaches for achieving it and one on how people who tried each option fared.' : ''}
For each, list 4-6 concrete search angles: specific queries including insider vocabulary, specific sites/communities/databases, specific document types.`,
  { phase: 'Plan', schema: PLAN, effort: 'high' })
if (!plan) throw new Error('planning agent failed twice')
log(`Plan: ${plan.subquestions.length} sub-questions; field: ${plan.field}`)

// =====================================================================
// RESEARCH helpers
// =====================================================================
const RESEARCH_MANDATES = {
  primary: 'PRIMARY/OFFICIAL mandate: official documentation, standards, filings, datasets, papers, original announcements, the authors\' own words. Establish the documented facts and numbers.',
  community: 'COMMUNITY mandate: what practitioners and real users say. Mine Reddit, Hacker News, Stack Exchange, GitHub issues/discussions, Discourse forums, Discord archives, YouTube, review sites, niche blogs. Capture experiences, complaints, workarounds, alternatives, insider vocabulary, dissent, and many verbatim voices.',
  contrarian: 'CONTRARIAN mandate: hunt the strongest counter-evidence. Who disagrees, what failed, what the mainstream take omits, rebuttals, retractions, "this is wrong because", people who tried it and regretted it, adjacent fields that see it differently.',
}

const researcher = (sq, mandate, round) => spawn(`You are one of three researchers on sub-question ${sq.id} of a deep research investigation into:
"${plan.restated_question}"
${OBJECTIVE_NOTE}
${EXAMPLES.length ? `The user's example(s) (${EXAMPLES.join('; ')}) only illustrate the category; unless your sub-question is about them, cover the broader set.` : ''}

SUB-QUESTION: ${sq.question}
${sq.why ? `Why it matters: ${sq.why}` : ''}
Starting angles: ${sq.search_angles.join(' | ')}

${RESEARCH_MANDATES[mandate]}

${TOOLS_NOTE}

${SOURCE_RULES}

${LEAD_RULES}
${mandate === 'community' ? `\n${FORUM_RULES}\n\n${PLATFORM_RECIPES}` : ''}

Standards: run at least ${MIN_SEARCHES} distinct searches (list them in searches_run), open and read at least ${MIN_SOURCES} distinct sources in full (list every URL in sources_read), return at least 10 claims with verbatim quotes. Mark key=true on claims the final answer or a recommendation depends on. Capture numbers and dated events. Note contradictions between sources.`,
  { phase: 'Research', label: `research:r${round}:${sq.id}:${mandate}`, schema: FINDINGS })

function mergeFindings(list) {
  const f = list.filter(Boolean)
  if (!f.length) return null
  const cat = k => f.flatMap(x => x[k] || [])
  return { summary: f.map(x => x.summary).join('\n\n'), claims: cat('claims'), voices: cat('voices'), numbers: cat('numbers'), timeline: cat('timeline'), contradictions: cat('contradictions'), unanswered: cat('unanswered'), leads: cat('leads'), sources_read: cat('sources_read'), searches_run: cat('searches_run'), coverage_note: f.map(x => x.coverage_note || '').filter(Boolean).join(' / ') }
}

async function researchTrio(sq, round) {
  const trio = await parallel(['primary', 'community', 'contrarian'].map(m => () => researcher(sq, m, round)))
  let merged = mergeFindings(trio)
  if (!merged) return null
  const hosts = new Set(merged.sources_read.map(host).filter(Boolean))
  if (merged.claims.length < 10 || hosts.size < 5) {
    log(`${sq.id}: thin (${merged.claims.length} claims, ${hosts.size} hosts); dispatching second pass`)
    const second = await spawn(`Second-pass researcher. The first pass on this sub-question was thin (${merged.claims.length} claims from ${hosts.size} distinct sites).
QUESTION: "${plan.restated_question}"
SUB-QUESTION ${sq.id}: ${sq.question}
Already read (do NOT repeat these URLs): ${[...new Set(merged.sources_read)].join(', ')}
Already found: ${merged.claims.map(c => c.claim).join(' | ')}
${TOOLS_NOTE}
${SOURCE_RULES}
${LEAD_RULES}
${PLATFORM_RECIPES}
Find what they missed: new sites, new phrasings, insider vocabulary, other communities, primary documents. At least ${MIN_SEARCHES} searches, ${MIN_SOURCES} new sources, 10 new claims.`, { phase: 'Research', label: `research:r${round}:${sq.id}:second`, schema: FINDINGS })
    merged = mergeFindings([merged, second])
  }
  return merged
}

// ---- leads ----
const entityKey = l => ((l.canonical_url ? normUrl(l.canonical_url) : '') + '|' + (l.name || '')).toLowerCase().replace(/[^a-z0-9|]+/g, '')

function harvestLeads(newEntries) {
  const byKey = new Map()
  for (const e of newEntries) for (const l of e.leads || []) {
    if (!l || !l.name) continue
    const k = entityKey(l)
    if (swarmed.has(k) || swarmedNames.has((l.name || '').toLowerCase().trim())) continue
    const prev = byKey.get(k)
    if (!prev) byKey.set(k, { ...l, key: k, reporters: [e.id], found_in: l.found_in || [], depth: e.depth || 0 })
    else {
      prev.reporters.push(e.id)
      prev.mention_count = (prev.mention_count || 1) + (l.mention_count || 1)
      prev.found_in.push(...(l.found_in || []))
      prev.contested = prev.contested || l.contested
      if (l.relevance === 'central') prev.relevance = 'central'
      prev.depth = Math.min(prev.depth, e.depth || 0)
    }
  }
  for (const l of byKey.values()) {
    let s = 0
    if (new Set(l.reporters).size >= 2) s += 3
    if (l.relevance === 'central') s += 2; else if (l.relevance === 'supporting') s += 1
    if (l.contested) s += 2
    if ((l.mention_count || 0) >= 3) s += 1
    if (['thread', 'community', 'tool', 'document'].includes(l.entity_type)) s += 1
    if (l.hops_taken === 0) s += 1
    l.prescore = s
  }
  return [...byKey.values()].sort((a, b) => b.prescore - a.prescore)
}

// ---- swarm angle sets ----
const ANGLES = {
  thread: [
    ['top', 'Read the WHOLE thread sorted by top/best, every page, expanding every collapsed chain.'],
    ['new-controversial', 'Read the WHOLE thread sorted by new and then by controversial: late corrections, OP updates, the dissent the top sort buries.'],
    ['links', 'Collect every outbound link in the thread (OP and comments), open each, record what it actually says vs how the commenter characterised it.'],
    ['primary-sources', 'For the 5-10 most repeated factual claims in the thread, find the original source (docs, paper, filing, commit, announcement) and quote it.'],
    ['cross-community', 'Search this thread\'s topic and insider vocabulary across every other community (other subreddits, HN, SE, Discourse forums, GitHub, YouTube, blogs); report agreement and disagreement with this thread\'s consensus. Open at least 15 other threads.'],
    ['contrarian', 'Hunt rebuttals: "this is wrong because", later threads revisiting the topic, people who tried it and failed, experts who disagree.'],
    ['credibility', 'Profile the 8-12 most influential commenters: account age, karma/trust, flair, domain post history, self-disclosed affiliation, whether their claims were later corrected.'],
    ['timeline', 'When was the thread; what changed since (versions, policies, newer threads); is the consensus still current as of today?'],
    ['siblings', 'Find the same community\'s other threads on this topic across years (5+ phrasings, sorted top and new, paginate) and show how the consensus moved.'],
    ['quant', 'Extract every number, price, benchmark, date and version in the thread into numbers[], with who said it and whether it was challenged.'],
  ],
  community: [
    ['canon', 'Wiki, sidebar, FAQ, pinned posts and rules of the community: what it treats as settled.'],
    ['top-alltime', 'Top posts of all time on the topic (5+ search phrasings, sorted top, paginate all results).'],
    ['top-recent', 'Top posts of the last 12 months on the topic; what is new or changing.'],
    ['new', 'Newest posts on the topic sorted by new: unresolved questions, fresh complaints.'],
    ['recurring', 'Extract the recurring claims with distinct-user support/dissent counts across the threads you read.'],
    ['dissent', 'Catalogue the dissenters and minority views, with their strongest quotes and credibility.'],
    ['power-users', 'Profile moderators and the most-cited power users: expertise, affiliations, incentives.'],
    ['siblings', 'Sibling communities on the same topic and how they differ from this one.'],
    ['timeline', 'Timeline of how the community\'s consensus shifted over the years.'],
    ['quant', 'Every number, price, benchmark, date anyone states, with who and whether challenged.'],
  ],
  tool: [
    ['official', 'Official docs, changelog/releases, pricing, licensing, stated limitations.'],
    ['issues', 'GitHub (or tracker) issues and discussions: top-reacted open bugs, closed-wontfix, maintainer responses, release cadence, bus factor.'],
    ['sentiment', 'Community sentiment sweep across Reddit/HN/forums, top and new, across years, with voices.'],
    ['comparisons', 'Head-to-head comparisons against named alternatives, with the criteria people use.'],
    ['failures', 'Failure and horror stories, migrations away, "we switched from X because".'],
    ['maker', 'Maker/company background: funding, business model, ownership changes, incentives, trust signals.'],
    ['adoption', 'Adoption/traction evidence: downloads, stars trajectory, job posts, case studies, who uses it.'],
    ['security-legal', 'Security, compliance and legal incidents or concerns.'],
    ['expert-reviews', 'Expert/longform reviews and benchmarks.'],
    ['credibility', 'Profile the loudest advocates and critics: affiliations, incentives, track record.'],
    ['quant', 'Every number (prices, benchmarks, limits, versions, dates) into numbers[], with source and whether challenged.'],
  ],
  person: [
    ['own-words', 'Their own writings, talks, repos, posts in full.'],
    ['interviews', 'Interviews and podcasts (transcripts).'],
    ['reception', 'What others say about them: praise and criticism, with voices.'],
    ['incentives', 'Conflicts of interest, affiliations, business incentives.'],
    ['track-record', 'Past claims/predictions and how they aged.'],
    ['network', 'Network and affiliations; who amplifies them and why.'],
    ['timeline', 'Timeline of their involvement with this topic.'],
    ['cross-community', 'Mentions across communities and how different communities view them.'],
    ['primary-sources', 'Primary sources behind their headline claims.'],
  ],
  term: [
    ['origin', 'Origin and canonical definition: first use, defining paper/doc.'],
    ['variants', 'Variants and competing definitions; where they conflict.'],
    ['literature', 'Academic/technical literature using the term.'],
    ['practice', 'How practitioners actually use it in forums; what it implies for them.'],
    ['critiques', 'Critiques: "this term is misleading", misuse, hype.'],
    ['measurement', 'How it is measured or quantified, with numbers.'],
    ['adjacent', 'Equivalents in adjacent fields.'],
    ['timeline', 'Timeline of the term\'s adoption and shifts in meaning.'],
  ],
  document: [
    ['full-read', 'Read the full document: all sections, tables, appendices, supplementary material.'],
    ['methods', 'Methodology and limitations as stated by the authors, and as critics see them.'],
    ['citers', 'Who cites it and for what; do they characterise it correctly?'],
    ['replication', 'Replications, critiques, retractions, errata.'],
    ['followups', 'The authors\' follow-ups and later work.'],
    ['coverage', 'Press and forum coverage vs what the document actually says.'],
    ['data', 'Data/code availability and what the data shows.'],
    ['competitors', 'Competing documents/studies on the same question.'],
    ['credibility', 'Authors, funders and their incentives.'],
  ],
  event: [
    ['primary', 'Timeline from primary statements and official records.'],
    ['reporting', 'Independent reporting.'],
    ['eyewitness', 'Forum eyewitness/participant accounts, with voices.'],
    ['response', 'Official responses and post-mortems.'],
    ['aftermath', 'Aftermath and consequences.'],
    ['disputed', 'Disputed facts and competing narratives.'],
    ['precedents', 'Similar prior incidents.'],
    ['quant', 'Every number and date, with source and whether challenged.'],
  ],
}
ANGLES.org = ANGLES.person
ANGLES.dataset = ANGLES.document
ANGLES.other = ANGLES.tool
const anglesFor = type => { const a = ANGLES[type] || ANGLES.other; return MAX ? a.slice(0, 12) : a.slice(0, Math.min(6, a.length)) }

let swarmCounter = 0
async function runSwarm(lead, decision, round) {
  const key = lead.key
  const angles = anglesFor(lead.entity_type)
  const depth = (lead.depth || 0) + 1
  swarmCounter++
  const swarmId = `SW${swarmCounter}`
  swarmed.set(key, { name: lead.name, entity_type: lead.entity_type, depth, round, agents: angles.length + 1 })
  swarmedNames.add((lead.name || '').toLowerCase().trim())
  log(`Swarm ${swarmId}: ${lead.entity_type} "${lead.name}" with ${angles.length} agents (depth ${depth})`)
  const questions = (decision.questions_to_answer || []).map(q => `- ${q}`).join('\n')
  const results = (await parallel(angles.map(([angle, brief]) => () => spawn(`You are one agent in a deep-dive swarm investigating the ${lead.entity_type} "${lead.name}" for a research project on:
"${plan.restated_question}"
${OBJECTIVE_NOTE}
ENTITY: ${lead.name}${lead.canonical_url ? ` — ${lead.canonical_url}` : ''}
Why it matters: ${lead.lead}
What is unknown about it: ${lead.what_is_unknown || 'see questions'}
Questions this swarm must answer:
${questions || '- what exactly it is, who says what, what the evidence is, how it relates to the main question, what contradicts it'}

YOUR ANGLE (${angle}): ${brief}
Other agents cover the other angles; go deep on yours.

${TOOLS_NOTE}
${FORUM_RULES}
${PLATFORM_RECIPES}
${SOURCE_RULES}
${LEAD_RULES}

Exhaustive coverage of your angle, not a summary. Fetch at least 10 pages (list them in sources_read). Return at least 8 claims with verbatim quotes (key=true where the main question or a recommendation depends on them), recurring_claims with distinct-user counts, 10-30 voices with credibility signals, every number, contradictions and who had the better of each argument, new leads, and an exact coverage_note. In answers[], answer each swarm question from your angle's evidence.`,
    { phase: 'Swarm', label: `swarm:r${round}:${swarmId}:${angle}`, schema: SWARM_FINDINGS })))).filter(Boolean)
  if (!results.length) return []
  const newEntries = []
  results.forEach(r => { const e = absorb(r, { kind: 'swarm', ref: `${swarmId}:${r.angle || 'angle'}`, question: `Deep dive: ${lead.name} (${r.angle})`, round, entity: lead.name, depth }); if (e) newEntries.push(e) })
  const dossier = await spawn(`You are the dossier compiler for the ${lead.entity_type} "${lead.name}". Below are the reports of ${results.length} swarm agents, each from a different angle. Synthesise ONE dossier: what it is (400-1000 words), consensus claims, dissent, primary sources, credibility assessment, how it relates to the question "${plan.restated_question}", open questions, and recommended follow-up leads (structured). Do not add facts not in the reports.

${results.map(r => `=== Angle: ${r.angle} ===\n${r.summary}\nAnswers: ${(r.answers || []).map(a => `${a.question} -> ${a.answer}`).join(' | ')}\nRecurring: ${(r.recurring_claims || []).map(x => `${x.claim} (+${x.supporters}/-${x.dissenters})`).join('; ')}\nContradictions: ${(r.contradictions || []).join('; ')}\nCoverage: ${r.coverage_note}`).join('\n\n')}`,
    { phase: 'Swarm', label: `swarm:r${round}:${swarmId}:dossier`, schema: DOSSIER, effort: 'high' })
  if (dossier) {
    dossiers.push({ ...dossier, swarm_id: swarmId, depth, entity_key: key })
    newEntries.push({ id: `${swarmId}:dossier`, kind: 'dossier', round, depth, entity: lead.name, question: '', summary: dossier.one_paragraph, claim_ids: [], unanswered: dossier.open_questions || [], contradictions: [], leads: dossier.recommended_followups || [] })
  }
  return newEntries
}

// ---- verification ----
async function verifyPending(tag) {
  const pending = claims.filter(c => c.status === 'pending')
  if (!pending.length) return
  log(`Verify: quote-checking ${pending.length} claims`)
  const checkChunks = chunk(pending, CHUNK)
  const checks = (await parallel(checkChunks.map((ch, i) => () => spawn(`You are a citation checker. For each claim below: open the URL (if blocked, try Wayback https://web.archive.org/web/2/<url>, archive.ph, or https://r.jina.ai/<url>, and record archive_url_used). Report whether the quote exists on the page verbatim/near-verbatim, whether the page actually supports the claim (not out of context), and the page date. Be strict: your job is to catch overstated or fabricated citations. Never mark a page you could not open as supporting anything. Check ALL ${ch.length} claims; return one entry per claim_id.
${TOOLS_NOTE}

${ch.map(c => `${c.id}\n  claim: ${c.claim}\n  url: ${c.url}\n  quote: "${c.quote}"`).join('\n')}`,
    { phase: 'Verify', label: `quotecheck:${tag}:${i}`, schema: QUOTE_CHECKS })))).filter(Boolean).flatMap(r => r.checks)
  const checkById = new Map(checks.map(k => [k.claim_id, k]))
  for (const c of pending) {
    const k = checkById.get(c.id)
    if (!k) { c.notes.push('quote-check: no result'); continue }
    if (k.page_date && !c.published) c.published = k.page_date
    if (k.archive_url_used) c.access_note = `via ${k.archive_url_used}`
    if (!k.reachable || k.quote_found === 'not_found' || k.supports_claim === 'no' || k.supports_claim === 'out_of_context') { c.status = 'citation_failed'; c.notes.push(`quote-check: reachable=${k.reachable}, quote=${k.quote_found}, supports=${k.supports_claim}${k.note ? ' — ' + k.note : ''}`) }
    else if (k.quote_found === 'paraphrase_only' || k.supports_claim === 'partially') c.notes.push(`quote-check: ${k.quote_found}, supports=${k.supports_claim}${k.note ? ' — ' + k.note : ''}`)
  }
  // re-source failed citations
  const failed = pending.filter(c => c.status === 'citation_failed')
  if (failed.length && governor.allowsFollowup()) {
    log(`Verify: re-sourcing ${failed.length} failed citations`)
    const fixes = (await parallel(chunk(failed, CHUNK).map((ch, i) => () => spawn(`You are a re-sourcer. These claims failed citation checks (the URL did not support them or the quote was not found). For each, find a URL that genuinely supports the claim with a verbatim quote, or report that you could not. Return findings with one claim per input claim (same wording), each with its new url/quote/title; omit claims you could not source. Put the input claim id at the start of each claim text in square brackets, e.g. "[C0012] ...".
${TOOLS_NOTE}
${SOURCE_RULES}
${ch.map(c => `${c.id}: ${c.claim} (failed source: ${c.url})`).join('\n')}`,
      { phase: 'Verify', label: `resource:${tag}:${i}`, schema: FINDINGS })))).filter(Boolean).flatMap(r => r.claims)
    const failedIds = new Set(failed.map(c => c.id))
    for (const f of fixes) {
      const m = (f.claim || '').match(/^\[(C\d{4})\]\s*/)
      const c = m && failedIds.has(m[1]) && claimById.get(m[1])
      if (!c || !f.url || !f.quote) continue
      const s = addSource(f); if (!s) continue
      c.notes.push(`re-sourced from ${c.url}`)
      Object.assign(c, { url: f.url, quote: f.quote, title: f.title || f.url, source_type: f.source_type || c.source_type, published: f.published || c.published, sid: s.id, status: 'pending' })
      s.claim_ids.push(c.id)
    }
  }
  // skeptic panels: independent corroboration for key claims; non-key claims that passed the quote-check are "source_checked"
  const passed = pending.filter(c => c.status === 'pending')
  const toJudge = passed.filter(c => c.key || c.source_type === 'community')
  passed.filter(c => !toJudge.includes(c)).forEach(c => { c.status = 'source_checked' })
  const n = governor.skeptics()
  if (!n) { toJudge.forEach(c => { c.status = 'source_checked'; c.notes.push('skeptic panel skipped: budget') }); return }
  log(`Verify: ${toJudge.length} key/community claims through ${n}-skeptic panels (${passed.length - toJudge.length} non-key claims source-checked only)`)
  const judgeChunks = chunk(toJudge, JUDGE_CHUNK)
  const panels = await parallel(judgeChunks.map((ch, i) => () => parallel(Array.from({ length: n }, (_, k) => () => spawn(`You are fact-checker #${k + 1} of ${n} on research into "${plan.restated_question}". Your job is to REFUTE the claims below, not to agree with them.
${TOOLS_NOTE}
For each claim: search for INDEPENDENT sources (not copies of the same original) that confirm or contradict it; check whether it is outdated as of today. Mark "confirmed" only with independent support (for community claims: several independent users or a primary source saying the same thing; a single anecdote is "unclear"). Mark "refuted" when independent evidence contradicts it, "outdated" when it was true but no longer is. Give the evidence_url for every verdict. Check ALL ${ch.length} claims; a missing claim_id counts against you.

${ch.map(c => `${c.id} [${c.source_type}${c.published ? ', ' + c.published : ''}] ${c.claim}\n  source: ${c.url}\n  quote: "${c.quote}"`).join('\n')}`,
    { phase: 'Verify', label: `skeptic:${tag}:${i}:${k + 1}`, schema: VERDICTS })))))
  const needAdjudication = []
  judgeChunks.forEach((ch, i) => {
    const votes = (panels[i] || []).filter(Boolean).flatMap(p => p.verdicts)
    for (const c of ch) {
      const vs = votes.filter(v => v.claim_id === c.id)
      vs.forEach(v => c.notes.push(`${v.status}: ${v.note}${v.evidence_url ? ` (${v.evidence_url})` : ''}`))
      if (!vs.length) { c.status = 'source_checked'; c.notes.push('no skeptic verdicts returned'); continue }
      const count = s => vs.filter(v => v.status === s).length
      const top = ['refuted', 'outdated', 'confirmed', 'unclear'].map(s => [s, count(s)]).sort((a, b) => b[1] - a[1])[0]
      const unanimous = top[1] === vs.length && vs.length >= Math.min(2, n)
      if (unanimous && top[0] !== 'unclear') c.status = top[0]
      else needAdjudication.push(c)
    }
  })
  if (needAdjudication.length) {
    log(`Verify: adjudicating ${needAdjudication.length} split verdicts`)
    const adj = (await parallel(chunk(needAdjudication, JUDGE_CHUNK).map((ch, i) => () => spawn(`You are the adjudicator. Fact-checkers split on the claims below. Read their notes, open at least one independent source per claim yourself, and return a decisive status: confirmed, refuted, outdated, or unclear (only if the evidence genuinely cannot settle it). Give evidence_url and a note explaining the decision. Return one verdict per claim_id.
${TOOLS_NOTE}
${ch.map(c => `${c.id}: ${c.claim}\n  source: ${c.url} — "${c.quote}"\n  votes: ${c.notes.join(' | ')}`).join('\n\n')}`,
      { phase: 'Verify', label: `adjudicate:${tag}:${i}`, schema: VERDICTS, effort: 'high' })))).filter(Boolean).flatMap(r => r.verdicts)
    const byId = new Map(adj.map(v => [v.claim_id, v]))
    for (const c of needAdjudication) {
      const v = byId.get(c.id)
      if (v) { c.status = v.status === 'unclear' ? 'contested' : v.status; c.notes.push(`adjudicator: ${v.status} — ${v.note}${v.evidence_url ? ` (${v.evidence_url})` : ''}`) }
      else c.status = 'contested'
    }
  }
}

// =====================================================================
// ROUND LOOP
// =====================================================================
let queue = plan.subquestions
let round = 0
let carryEntries = []
while (round < MAX_ROUNDS && (queue.length || carryEntries.length)) {
  round++
  phase('Research')
  log(`Round ${round}: ${queue.length} sub-questions`)
  queue.forEach(sq => seenSubq.push(sq.question))
  const results = await parallel(queue.map(sq => () => researchTrio(sq, round)))
  const roundEntries = []
  results.forEach((f, i) => { const e = absorb(f, { kind: 'subquestion', ref: queue[i].id, question: queue[i].question, round, depth: 0 }); if (e) roundEntries.push(e) })
  log(`Round ${round}: ${claims.filter(c => c.status === 'pending').length} new claims from research`)

  // ---- lead triage + swarms ----
  phase('Swarm')
  const leads = harvestLeads([...roundEntries, ...carryEntries])
  carryEntries = []
  let swarmEntries = []
  if (leads.length && governor.allowsFollowup()) {
    const rows = leads.map(l => `${l.key} | score ${l.prescore} | ${l.entity_type} | ${l.name} | ${l.canonical_url || '-'} | reporters ${[...new Set(l.reporters)].join(',')} | mentions ${l.mention_count} | ${l.relevance} | contested ${!!l.contested} | hops ${l.hops_taken} | depth ${l.depth} | unknown: ${l.what_is_unknown}`).join('\n')
    const swarmCap = Math.max(0, Math.min(SWARMS_PER_ROUND, MAX_SWARMS - swarmed.size))
    const triage = await spawn(`You are the lead triage officer for a deep research investigation into:
"${plan.restated_question}"
${OBJECTIVE_NOTE}

Researchers found the leads below (entities they noticed but did not exhaust). For each decide:
- "swarm": worth ${MAX ? '8-12' : '5-6'} dedicated agents that will read EVERYTHING about it (every page of the thread, every link, every other community's take, the primary sources behind it, the dissenters). Use this when the entity could change the answer or a recommendation, when several researchers independently hit it, when sources disagree about it, when it is a container with real depth (a long thread, a tool with its own ecosystem, a study many cite, a person whose claims drive the discussion), or when insiders treat it as common knowledge the outside literature ignores.
- "followup": one agent, one or two hops, to pin down a specific fact.
- "park": record as unexplored; not worth the effort now.
Rules: pre-scores >= 6 may not be parked. Leads at depth >= ${MAX_DEPTH} may not be swarmed (followup or park only). At most ${governor.allowsSwarm() ? swarmCap : 0} swarms this round; prefer diversity of entity types over many threads about the same thing. For every non-parked lead write 3-8 concrete questions the agents must answer about it.

LEADS (key | pre-score | type | name | url | reporters | mentions | relevance | contested | hops | depth | unknowns):
${rows}
Already swarmed (do not repeat): ${[...swarmed.values()].map(v => v.name).join(', ') || 'none'}`,
      { phase: 'Swarm', label: `triage:r${round}`, schema: TRIAGE, effort: 'high' })
    const leadByKey = new Map(leads.map(l => [l.key, l]))
    const decisions = (triage ? triage.decisions : []).filter(d => leadByKey.has(d.key))
    const decided = new Set(decisions.map(d => d.key))
    // script floor: hot leads the triage ignored become follow-ups
    leads.filter(l => !decided.has(l.key) && l.prescore >= 6).forEach(l => decisions.push({ key: l.key, tier: 'followup', why: 'script floor: high pre-score left undecided', questions_to_answer: [l.what_is_unknown] }))
    const namesThisRound = new Set()
    const swarmDecisions = governor.allowsSwarm() ? decisions.filter(d => {
      const l = leadByKey.get(d.key); const nm = (l.name || '').toLowerCase().trim()
      if (d.tier !== 'swarm' || l.depth >= MAX_DEPTH || namesThisRound.has(nm)) return false
      namesThisRound.add(nm); return true
    }).slice(0, swarmCap) : []
    const followups = decisions.filter(d => d.tier === 'followup' || (d.tier === 'swarm' && !swarmDecisions.includes(d)))
    decisions.filter(d => d.tier === 'park').forEach(d => parked.push({ ...leadByKey.get(d.key), why_parked: d.why, round }))
    leads.filter(l => !decided.has(l.key) && l.prescore < 6).forEach(l => parked.push({ ...l, why_parked: 'not selected by triage', round }))
    log(`Triage r${round}: ${swarmDecisions.length} swarms, ${followups.length} follow-ups, ${parked.filter(p => p.round === round).length} parked`)

    const swarmResults = await parallel(swarmDecisions.map(d => () => runSwarm(leadByKey.get(d.key), d, round)))
    swarmEntries = swarmResults.filter(Boolean).flat()
    const fuResults = await parallel(followups.map(d => () => {
      const l = leadByKey.get(d.key)
      return spawn(`Follow-up researcher on a lead found during research into "${plan.restated_question}".
LEAD: ${l.name} (${l.entity_type})${l.canonical_url ? ` — ${l.canonical_url}` : ''}
Why: ${l.lead}
Questions to answer:
${(d.questions_to_answer || []).map(q => `- ${q}`).join('\n')}
${TOOLS_NOTE}
${SOURCE_RULES}
${LEAD_RULES}
${PLATFORM_RECIPES}
Two hops max, but thorough on those hops: open at least 6 sources, return every claim with quotes, voices, numbers, and any new leads.`, { phase: 'Swarm', label: `followup:r${round}:${d.key.slice(0, 40)}`, schema: FINDINGS })
    }))
    fuResults.forEach((f, i) => { const l = leadByKey.get(followups[i].key); const e = absorb(f, { kind: 'followup', ref: `FU-r${round}-${i + 1}`, question: `Follow-up: ${l.name}`, round, entity: l.name, depth: (l.depth || 0) + 1 }); if (e) swarmEntries.push(e) })
  }
  carryEntries = swarmEntries   // their leads enter next round's triage at depth+1

  // ---- verify everything new ----
  phase('Verify')
  await verifyPending(`r${round}`)
  const st = stats()
  log(`After round ${round}: ${claims.length} claims (${Object.entries(st).map(([k, v]) => `${k} ${v}`).join(', ')}), ${sources.size} sources, ${swarmed.size} swarms, ${voices.length} voices`)

  if (round >= MAX_ROUNDS) break

  // ---- director + stop auditor ----
  phase('Direct')
  const compact = claims.map(claimLine).join('\n')
  const digest = entries.filter(e => e.kind !== 'dossier').map(e => `## ${e.id} (${e.kind}, r${e.round}): ${e.question}\n${e.summary.slice(0, 1500)}\nUnanswered: ${e.unanswered.join('; ') || 'none'}\nContradictions: ${e.contradictions.join('; ') || 'none'}`).join('\n\n')
  const dossierDigest = dossiers.map(d => `- ${d.name} (${d.entity_type}): ${d.one_paragraph}\n  open: ${d.open_questions.join('; ')}`).join('\n')
  const common = `Investigation: "${plan.restated_question}"
${OBJECTIVE_NOTE}
${EXAMPLES_NOTE}
Today: ${TODAY}. Round ${round} of at most ${MAX_ROUNDS} is complete (minimum ${MIN_ROUNDS}).

SUB-QUESTIONS RESEARCHED SO FAR (do not propose anything overlapping >50% with these):
${seenSubq.map(q => `- ${q}`).join('\n')}

ENTITY DOSSIERS:
${dossierDigest || 'none yet'}

FINDINGS DIGEST:
${digest}

CLAIM LEDGER (id [status] [source type, date] claim — source):
${compact}`
  const [director, auditor] = await parallel([
    () => spawn(`You are the research director.
${common}

Decide what to research next so the final answer is complete and trustworthy. Consider: unanswered items; refuted/contested/citation-failed claims that need better evidence; missing counter-evidence; missing quantitative data; missing recent developments; perspectives and communities not yet represented; dots that connect across sub-questions and dossiers (if two findings together suggest something new, investigate it).${EXAMPLES.length ? ` Check for anchoring on the user's example(s) and broaden if needed.` : ''}
Rate coverage on each dimension. Return up to ${MAX ? 8 : 5} NEW sub-questions with 4-6 concrete search angles each. Set done=true only if every dimension is at least adequate and nothing material is missing.`,
      { phase: 'Direct', label: `director:r${round}`, schema: GAPS, effort: 'high' }),
    () => spawn(`You are the stop auditor. Your job is to argue that this research is NOT done. A hostile expert reviewer in the field "${plan.field}" will read the final report: list everything they would say is missing, thin, one-sided, outdated or unverified, and turn the most important gaps into up to ${MAX ? 6 : 4} new sub-questions with concrete search angles. Rate coverage honestly on each dimension. Set done=true only if you genuinely cannot find a material gap.
${common}`,
      { phase: 'Direct', label: `stopaudit:r${round}`, schema: GAPS, effort: 'high' }),
  ])
  const norm = s => s.toLowerCase().replace(/[^a-z0-9 ]+/g, ' ').split(/\s+/).filter(w => w.length > 3)
  const overlaps = (a, b) => { const A = new Set(norm(a)), B = new Set(norm(b)); const inter = [...A].filter(w => B.has(w)).length; return inter / Math.max(1, Math.min(A.size, B.size)) > 0.5 }
  const proposed = [...(director ? director.new_subquestions : []), ...(auditor ? auditor.new_subquestions : [])]
  const fresh = []
  for (const sq of proposed) { if (!seenSubq.some(q => overlaps(q, sq.question)) && !fresh.some(f => overlaps(f.question, sq.question))) fresh.push(sq) }
  queue = fresh.map((sq, i) => ({ ...sq, id: `R${round + 1}-${i + 1}` }))
  const thin = g => g && Object.values(g.coverage_assessment || {}).some(v => v === 'thin')
  const bothDone = director && auditor && director.done && auditor.done && !thin(director) && !thin(auditor)
  log(`Direct r${round}: director done=${director ? director.done : 'n/a'}, auditor done=${auditor ? auditor.done : 'n/a'}, ${queue.length} new sub-questions, ${carryEntries.length} entries carrying leads`)
  if (round >= MIN_ROUNDS && bothDone && !queue.length) break
  if (!queue.length && !carryEntries.length) {
    if (round < MIN_ROUNDS) queue = [{ id: `R${round + 1}-1`, question: `What important aspects of "${plan.restated_question}" has the research so far missed? Find them.`, search_angles: ['lateral searches', 'adjacent fields', 'newest sources', 'communities not yet covered'] }]
    else break
  }
}
const unresearched = queue.map(q => q.question)
if (unresearched.length) log(`Stopped after ${round} rounds with ${unresearched.length} proposed sub-question(s) unresearched`)

// =====================================================================
// WRITE
// =====================================================================
phase('Write')
const usable = claims.filter(c => c.status !== 'citation_failed')
const compactLedger = usable.map(claimLine).join('\n')
const skeleton = `Required skeleton (instantiate all; add theme sections as needed; split any section whose claim_ids exceed ~40):
1. scope — Scope, definitions and the question as researched (assumptions, exclusions, examples vs category) — 600+ words
2. landscape — Landscape / background (the field, the players, the history to today) — 1500+
3+. theme-* — one section per theme (typically ${MAX ? '7-10' : '5-8'}; 1200-2500 words each): every relevant confirmed claim, contested ones labelled, community voices inline, a table wherever 4+ items compare
then. deep-* — one section per entity dossier whose relation_to_question is not tangential (800-2000 words each)
then. quant — Quantitative picture (every number with date, source, whether challenged; tables) — 800+
then. disagreements — Where the evidence disagrees, and why (each disagreement: sides, best evidence, likely reason, assessment) — 1000+
then. debunked — Debunked, outdated and unverifiable (every refuted/outdated claim, who repeats it; every contested claim and what would settle it) — 800+
then. practitioners — What practitioners say: community evidence by community, with spread and era — 1200+
${OBJECTIVE ? 'then. recommendations — Ranked options table, then one subsection per option (pros, cons, cost/effort, risks, prerequisites, who it suits, evidence IDs), "if you only do one thing", next steps — 1500+\n' : ''}then. trail — Discovery trail: how one lead led to another, what the swarms found that the plan did not anticipate — 800+
then. unknowns — Unknowns and open leads — 600+
then. confidence — Confidence assessment per major conclusion (verification counts behind it, weakest link) — 500+
Total body minimum: ${MIN_BODY_WORDS} words. Distribute min_words/target_words so the sum of target_words is at least ${Math.round(MIN_BODY_WORDS * 1.15)}. Executive summary and glossary are written separately; do not include them.`

const outline = await spawn(`You are the outline editor for a very long, exhaustive research report on:
"${plan.restated_question}"
${OBJECTIVE_NOTE}
${EXAMPLES_NOTE}

${skeleton}

Assign EVERY claim id below to at least one section (a claim may appear in several). Theme sections should group claims by subject, not by which sub-question found them. For each section give purpose, must_cover (3+ items), required tables, dossier_names it should draw on, a voice_filter describing which community voices belong, min_words and target_words.

ENTITY DOSSIERS: ${dossiers.map(d => `${d.name} (${d.entity_type}; relation: ${d.relation_to_question.slice(0, 200)})`).join(' | ') || 'none'}
SUB-QUESTIONS: ${entries.filter(e => e.kind === 'subquestion').map(e => `${e.id}: ${e.question}`).join(' | ')}
VOICES available: ${voices.length}; NUMBERS: ${numbers.length}; TIMELINE entries: ${timeline.length}

CLAIM LEDGER:
${compactLedger}`, { phase: 'Write', label: 'outline', schema: OUTLINE, effort: 'high' })
if (!outline) throw new Error('outline agent failed twice')
// make sure every usable claim lands somewhere
const assigned = new Set(outline.sections.flatMap(s => s.claim_ids))
const orphans = usable.filter(c => !assigned.has(c.id)).map(c => c.id)
if (orphans.length) { const tgt = outline.sections.find(s => /theme/i.test(s.id)) || outline.sections[1] || outline.sections[0]; tgt.claim_ids.push(...orphans); log(`Outline: ${orphans.length} unassigned claims added to "${tgt.title}"`) }
log(`Outline: ${outline.sections.length} sections, ${outline.sections.reduce((n, s) => n + (s.target_words || 0), 0)} target words`)

const sliceFor = spec => {
  const ids = new Set(spec.claim_ids)
  const cs = usable.filter(c => ids.has(c.id))
  const urls = new Set(cs.map(c => normUrl(c.url)))
  const ds = dossiers.filter(d => (spec.dossier_names || []).includes(d.name))
  const entityNames = ds.map(d => d.name)
  const tag = `${spec.id} ${spec.title}`
  const vs = voices.filter(v => urls.has(normUrl(v.url)) || entityNames.includes(v.entity) || /practitioner|voice|community/i.test(tag)).slice(0, 60)
  const ns = numbers.filter(n => urls.has(normUrl(n.url)) || /quant/i.test(tag)).slice(0, 120)
  const ts = /landscape|timeline|trail|history/i.test(tag) ? timeline.slice(0, 120) : timeline.filter(t => urls.has(normUrl(t.url))).slice(0, 40)
  return { cs, ds, vs, ns, ts }
}
const sliceText = ({ cs, ds, vs, ns, ts }) => `LEDGER SLICE (cite with [S#] tokens exactly as given, e.g. [${cs[0] ? cs[0].sid : 'S1'}]; claim ids as [C####]):
${cs.map(claimFull).join('\n')}

DOSSIERS:
${ds.map(d => `### ${d.name} (${d.entity_type})\n${d.what_it_is}\nConsensus: ${d.consensus_claims.join('; ')}\nDissent: ${d.dissent.join('; ')}\nPrimary sources: ${(d.primary_sources || []).join('; ')}\nCredibility: ${d.credibility_assessment}\nRelation to question: ${d.relation_to_question}\nOpen: ${d.open_questions.join('; ')}`).join('\n\n') || 'none'}

VOICES (verbatim community quotes; cite the [S#] token of a claim from the same URL where one exists, else give platform/author/date inline):
${vs.map(v => `- "${v.quote}" — ${v.author}, ${v.platform}, ${v.date || 'undated'}, ${v.stance}, credibility: ${v.credibility}${v.upvotes ? `, votes ${v.upvotes}` : ''} — ${v.url}`).join('\n') || 'none'}

NUMBERS:
${ns.map(n => `- ${n.what}: ${n.value} (${n.who || 'unattributed'}, ${n.date || 'undated'}${n.challenged ? ', CHALLENGED' : ''}) — ${n.url}`).join('\n') || 'none'}

TIMELINE:
${ts.map(t => `- ${t.date}: ${t.event}${t.url ? ` — ${t.url}` : ''}`).join('\n') || 'none'}`

const STATUS_LEGEND = `Status labels: confirmed = quote verified on the page AND independent fact-checkers found independent support; source_checked = quote verified on the cited page but not independently corroborated (non-key claims); contested = checkers split or evidence conflicts; refuted = independent evidence contradicts it; outdated = was true, no longer is. Source types: primary, secondary, community (forum/user reports), weak.`

const writerPrompt = (spec, others, slice, prev) => `You are writing ONE section of a very long, exhaustive research report. Other agents write the other sections; do not summarise the whole report or write a report introduction.
REPORT QUESTION: "${plan.restated_question}"
${OBJECTIVE_NOTE}
${EXAMPLES.length ? `The user's example(s) (${EXAMPLES.join('; ')}) were illustrations; write at the category level and use them only as data points.` : ''}
Today: ${TODAY}.

YOUR SECTION: ${spec.title} (id ${spec.id}) — ${spec.purpose}
Must cover: ${spec.must_cover.join('; ')}
Tables required: ${(spec.tables || []).join('; ') || 'any comparison of 4+ items'}
LENGTH: at least ${spec.min_words} words, target ${spec.target_words}. Depth is the point: a reader should finish knowing everything the team learned on this theme, including nuances, numbers, dissent and who said what. Do not compress; expand. Every relevant claim in your slice should appear.
Other sections (do not duplicate them): ${others}

Rules:
- Use ONLY the ledger slice, dossiers, voices, numbers and timeline below. No facts from memory.
- Cite every factual sentence with its source token [S#] (the exact token given for that source). You may add the claim id [C####]. Never write URLs or footnote numbers yourself; the script resolves tokens.
- ${STATUS_LEGEND} Build on confirmed and source_checked claims (say "source-checked" where a reader should know it is single-sourced); label contested ones "(contested: ...)"; state refuted/outdated ones only as debunked/outdated; label community evidence with its spread, e.g. "(community: r/x, 2023, ~12 users)".
- Quote community voices verbatim in block quotes with username, platform, date and the [S#] token where available; prefer firsthand experience and sharp dissent.
- Subheadings (###) every 300-500 words; tables for any comparison of 4+ items.
- Direct, specific register. No filler, no "it is important to note".
- Do not include the section's H2 heading; start with the body.
- Return an honest word_count.
${prev ? `\nYOUR PREVIOUS DRAFT was ${wc(prev.markdown)} words; the minimum is ${spec.min_words}. Expand it using the claims below that it did not use: ${slice.cs.filter(c => !(prev.claim_ids_used || []).includes(c.id)).map(c => c.id).join(', ') || '(use more detail, voices, numbers and tables)'}.\nPREVIOUS DRAFT:\n${prev.markdown}\n` : ''}
${sliceText(slice)}`

const othersLine = spec => outline.sections.filter(s => s.id !== spec.id).map(s => `${s.id}: ${s.title} — ${s.purpose}`).join(' | ')
let sections = await parallel(outline.sections.map(spec => () => (async () => {
  const slice = sliceFor(spec)
  let s = await spawn(writerPrompt(spec, othersLine(spec), slice, null), { phase: 'Write', label: `write:${spec.id}`, schema: SECTION, effort: 'high' })
  if (s && wc(s.markdown) < 0.9 * spec.min_words) {
    const s2 = await spawn(writerPrompt(spec, othersLine(spec), slice, s), { phase: 'Write', label: `write:${spec.id}:expand`, schema: SECTION, effort: 'high' })
    if (s2 && wc(s2.markdown) > wc(s.markdown)) s = s2
    if (wc(s.markdown) < 0.9 * spec.min_words) log(`Section ${spec.id} short: ${wc(s.markdown)}/${spec.min_words} words after expansion`)
  }
  return s ? { ...s, id: spec.id, title: spec.title, word_count: wc(s.markdown) } : null
})()))
sections = sections.filter(Boolean)
log(`Write: ${sections.length}/${outline.sections.length} sections, ${sections.reduce((n, s) => n + s.word_count, 0)} body words`)

const draftText = secs => secs.map(s => `## ${s.title} {#${s.id}}\n\n${s.markdown}`).join('\n\n')
const front = await spawn(`You are the stitching editor of a very long research report on "${plan.restated_question}". ${OBJECTIVE_NOTE}
Write (1) an executive summary of 600-1000 words: the direct answer, overall confidence, the top 10 findings with [S#] citations copied from the sections, the top recommendations if any, the biggest unknowns; (2) a "How to read this report" section (300+ words) explaining the status labels, source types, [C####] claim ids (Appendix A), confidence scale, and the methodology in brief (${round} rounds, ${entries.filter(e => e.kind === 'subquestion').length} sub-questions, ${swarmed.size} deep-dive swarms, ${claims.length} claims verified); (3) a 2-3 sentence bridge for each section id; (4) a glossary of every insider term, acronym, tool and named entity used in the report, 1-3 sentences each with [S#] where a source defines it.
${STATUS_LEGEND}
Cite only with [S#] tokens that appear in the draft.

DRAFT:
${draftText(sections)}`, { phase: 'Write', label: 'stitch', schema: FRONT, effort: 'high' })

// =====================================================================
// REVIEW LOOP
// =====================================================================
const sourceList = () => [...sources.values()].sort((a, b) => a.n - b.n)
const passes = governor.reviewPasses()
for (let pass = 1; pass <= passes; pass++) {
  phase('Review')
  log(`Review pass ${pass}/${passes}`)
  const draft = draftText(sections)
  const header = `Research question: "${plan.restated_question}"\n${OBJECTIVE_NOTE}\n${EXAMPLES_NOTE}\nToday: ${TODAY}. Field: ${plan.field}.\nReturn concrete, locatable issues each with the offending text quoted verbatim (<= 60 words), the section_id (from the "{#id}" marker in the heading), and a proposed replacement text. Do not return praise. Severity: critical = false or unsupported statement a reader would act on; major = materially misleading, missing or incoherent; minor = clarity/precision; nit = style. Prefix issue ids with your lens name.\n${STATUS_LEGEND}`
  const citedTokens = new Set((draft.match(/\[S\d+\]/g) || []).map(t => t.slice(1, -1)))
  const citedSources = sourceList().filter(s => citedTokens.has(s.id))
  const lenses = [
    ['completeness', `You are the completeness reviewer. The ledger below is everything the team found; the report should use ALL of it that is relevant. List: confirmed/contested claims marked UNUSED that a reader would want (section + text to add); dossiers that got less than a full subsection; dissent, contradictions and refuted claims silently dropped (refuted ones should appear as debunked); numbers and timeline entries missing; sub-questions underrepresented relative to evidence volume; firsthand community voices not quoted anywhere. Major for any omission that changes understanding. The bar is exhaustive, not sufficient.\n\nLEDGER (UNUSED = neither the claim id nor its source token appears in the draft):\n${usable.map(c => `${claimLine(c)}${draft.includes(c.id) || draft.includes(`[${c.sid}]`) ? '' : ' — UNUSED'}`).join('\n')}\nDOSSIERS: ${dossiers.map(d => d.name).join(', ') || 'none'}\nVOICES not quoted: ${voices.filter(v => !draft.includes(v.quote.slice(0, 40))).length} of ${voices.length}`],
    ['anchoring', `You are the anchoring and bias reviewer. Check whether the report over-focuses on the user's illustrative examples or on the first entities found; presents the loudest community's view as the field's view; lets one source or one swarm dominate a section; frames contested claims as settled or settled ones as contested; uses confidence language inconsistent with the status labels; treats vendor/marketing sources as neutral; omits the strongest counter-case. Propose rebalanced text with the claim ids that support it.`],
    ['logic', `You are the logic reviewer. Find conclusions not supported by the cited claims; non-sequiturs; recommendations whose pros/cons do not follow from the evidence; internal contradictions between sections; causal claims resting on correlation or anecdote; unstated assumptions; places where "users report X" silently becomes "X is true".`],
    ['structure', `You are the structure editor. The report must be long and detailed, so your job is NOT to shorten it. Find sections that duplicate each other (propose merging content, never deleting evidence); missing signposting; lists of 4+ comparable items that should be tables; inconsistent terminology; headings not matching content; walls of text needing subheadings; glossary terms used before definition. Never propose cutting evidence or quotes.`],
    ['expert', `You are a senior practitioner with 20 years in the field "${plan.field}", reviewing this as a peer who expects the author to be an outsider. Where would you object? What does it get subtly wrong, oversimplify, or miss that an insider would raise immediately (standard caveats, well-known failure modes, trade-offs, regulatory or operational realities, the thing everyone in the field knows but nobody writes down)? Which claims need a stronger source? Which recommendations are naive? Where the ledger lacks the evidence for your fix, set needs_research=true with the exact research_question.`],
    ['numbers', `You are the quantitative consistency reviewer. Check every number, date, version, price and percentage against the numbers table and claim quotes: same figure, unit, date; same quantity given differently in two sections; aged figures not dated; ranges reported as points; forum-reported numbers not labelled as such.\n\nNUMBERS TABLE:\n${numbers.map(n => `- ${n.what}: ${n.value} (${n.who || '?'}, ${n.date || 'undated'}${n.challenged ? ', CHALLENGED' : ''}) — ${n.url}`).join('\n')}`],
    ['recency', `You are the recency reviewer. Today is ${TODAY}. For each key statement, check the dates of its sources and whether newer evidence in the ledger supersedes it; flag statements resting only on sources older than 18 months in a fast-moving area, and statements whose claims are marked outdated yet appear as current. Propose dated wording ("as of <date>") or replacement claims.\n\nCLAIM DATES:\n${usable.map(c => `${c.id} [${c.status}] ${c.published || 'undated'}: ${c.claim.slice(0, 120)}`).join('\n')}`],
    ['voices', `You are the community-evidence reviewer. For every statement attributed to users/forums: is it labelled as community evidence; does the report say how widespread it is (one user vs many, which communities, what era); are quotes verbatim and attributed with date; are dissenting voices represented alongside consensus; is any single anecdote inflated into a pattern; are the strongest firsthand quotes used where they would help?\n\nAVAILABLE VOICES:\n${voices.slice(0, 150).map(v => `- "${v.quote}" — ${v.author}, ${v.platform}, ${v.date || 'undated'}, ${v.stance}`).join('\n')}`],
    ...(OBJECTIVE ? [['recommendations', `You are the decision reviewer acting for the user, whose objective is: ${OBJECTIVE}. Are recommendations ranked with explicit criteria; does each have pros, cons, cost/effort, risks, prerequisites, who it suits and who it doesn't, and the claim ids behind it; are options the evidence supports missing; is there an "if you only do one thing" answer; are next steps concrete; does any recommendation rest on contested or refuted claims?`]] : []),
  ]
  const citeChunks = chunk(citedSources, 10)
  const reviews = await parallel([
    ...citeChunks.map((ch, i) => () => spawn(`${header}
You are a citation auditor (lens "citation"). For each source below: open the URL (Wayback/archive.ph/r.jina.ai if blocked), find every sentence in the draft that cites its token, and check whether the page actually supports each such sentence (not just the ledger quote taken out of context). Report an issue (critical for unsupported/out-of-context, major for partially supported or unreachable with no archive) for each failing sentence, with a proposed_fix that either softens the sentence to what the source supports or replaces the citation with another [S#] token from the draft that does support it. Never treat a source you could not open as supporting anything.
${TOOLS_NOTE}

SOURCES TO AUDIT:
${ch.map(s => `[${s.id}] ${s.title} — ${s.url}\n   ledger quotes: ${s.claim_ids.map(id => claimById.get(id)).filter(Boolean).map(c => `"${c.quote}"`).join(' / ')}`).join('\n')}

DRAFT:
${draft}`, { phase: 'Review', label: `review${pass}:cite:${i}`, schema: REVIEW })),
    ...lenses.map(([name, text]) => () => spawn(`${header}\nLens: ${name}.\n${text}\n\nDRAFT:\n${draft}`, { phase: 'Review', label: `review${pass}:${name}`, schema: REVIEW, effort: 'high' })),
  ])
  const allIssues = reviews.filter(Boolean).flatMap(r => r.issues.map(i => ({ ...i, lens: r.lens })))
  const triage = allIssues.length ? await spawn(`You are the managing editor. ${allIssues.length} issues were raised by reviewers on the current draft of a research report on "${plan.restated_question}". Merge duplicates (keep the best proposed fix), reject issues that are wrong, out of scope, or would shorten the report without cause (explain why), keep everything else. Keep any citation-audit issue marked unsupported/out_of_context as critical. Set pass_verdict="publishable" only if no critical or major issues remain accepted.
${STATUS_LEGEND}

ISSUES:
${allIssues.map(i => `[${i.id}] (${i.lens}, ${i.severity}, section ${i.section_id}, needs_research=${i.needs_research})\n  text: "${i.offending_text}"\n  problem: ${i.problem}\n  fix: ${i.proposed_fix}${i.evidence_ids && i.evidence_ids.length ? `\n  evidence: ${i.evidence_ids.join(', ')}` : ''}${i.research_question ? `\n  research: ${i.research_question}` : ''}`).join('\n\n')}`,
    { phase: 'Review', label: `review${pass}:triage`, schema: REVIEW_TRIAGE, effort: 'high' }) : { accepted: [], rejected: [], pass_verdict: 'publishable' }
  const accepted = triage ? triage.accepted : []
  const blocking = accepted.filter(i => i.severity === 'critical' || i.severity === 'major')
  reviewLog.push({ pass, raised: allIssues.length, accepted: accepted.length, blocking: blocking.length, rejected: triage ? triage.rejected.length : 0, by_lens: Object.fromEntries(reviews.filter(Boolean).map(r => [r.lens, r.issues.length])) })
  log(`Review ${pass}: ${allIssues.length} raised, ${accepted.length} accepted (${blocking.length} blocking)`)
  if (!accepted.length) break
  if (!blocking.length && pass > 1) break

  // issues needing new evidence -> mini research -> verify
  const needEvidence = accepted.filter(i => i.needs_research && i.research_question)
  if (needEvidence.length && governor.allowsFollowup()) {
    const extra = await parallel(needEvidence.map((i, k) => () => spawn(`Gap researcher for a report on "${plan.restated_question}". A reviewer (${i.lens || 'review'}) flagged: ${i.problem}\nResearch question: ${i.research_question}\n${TOOLS_NOTE}\n${SOURCE_RULES}\n${PLATFORM_RECIPES}\nOpen at least 6 sources; return claims with verbatim quotes, voices, numbers.`, { phase: 'Review', label: `review${pass}:research:${k}`, schema: FINDINGS })))
    extra.forEach((f, k) => absorb(f, { kind: 'review-gap', ref: `RG${pass}-${k + 1}`, question: needEvidence[k].research_question, round, depth: 0 }))
    await verifyPending(`rev${pass}`)
  }
  // rewrite affected sections in parallel
  const bySection = {}
  for (const i of accepted) (bySection[i.section_id] = bySection[i.section_id] || []).push(i)
  const newIds = claims.filter(c => c.origin.kind === 'review-gap' && c.status !== 'citation_failed').map(c => c.id)
  const rewritten = await parallel(Object.entries(bySection).map(([sid, issues]) => () => {
    const sec = sections.find(s => s.id === sid); if (!sec) return Promise.resolve(null)
    const spec = outline.sections.find(s => s.id === sid) || { id: sid, title: sec.title, claim_ids: [], must_cover: [], min_words: sec.word_count, target_words: sec.word_count }
    const slice = sliceFor({ ...spec, claim_ids: [...spec.claim_ids, ...newIds] })
    return spawn(`You are rewriting section "${sec.title}" (id ${sid}) of a deep research report on "${plan.restated_question}" to resolve the accepted review issues below.
Rules: apply every fix; preserve all existing evidence, quotes and citations unless an issue says to remove them; keep the section at least as long as before (${sec.word_count} words) unless an issue explicitly calls for removal (then set length_reduction_justified=true); cite only with [S#] tokens from the ledger slice; do not introduce facts not in the slice; keep status and community labels. Do not include the H2 heading.
${STATUS_LEGEND}

ISSUES:
${issues.map(i => `- (${i.severity}) "${i.offending_text}" — ${i.problem} — FIX: ${i.proposed_fix}${i.evidence_ids && i.evidence_ids.length ? ` [evidence: ${i.evidence_ids.join(', ')}]` : ''}`).join('\n')}

CURRENT SECTION:
${sec.markdown}

${sliceText(slice)}`, { phase: 'Review', label: `review${pass}:rewrite:${sid}`, schema: SECTION, effort: 'high' })
  }))
  for (const r of rewritten.filter(Boolean)) {
    const idx = sections.findIndex(s => s.id === r.id)
    if (idx < 0) continue
    const newWc = wc(r.markdown)
    if (newWc >= 0.9 * sections[idx].word_count || r.length_reduction_justified) sections[idx] = { ...sections[idx], markdown: r.markdown, word_count: newWc }
    else log(`Review ${pass}: rejected rewrite of ${r.id} (shrank ${sections[idx].word_count} -> ${newWc} without justification)`)
  }
  if (triage && triage.pass_verdict === 'publishable' && pass > 1) break
}
const lastBlocking = reviewLog.length ? reviewLog[reviewLog.length - 1].blocking : 0

// =====================================================================
// ASSEMBLY (script)
// =====================================================================
const finalSources = sourceList()
const frontText = front ? `## Executive summary\n\n${front.executive_summary}\n\n## How to read this report\n\n${front.how_to_read}\n\n` : ''
const bridges = new Map(front ? front.bridges.map(b => [b.section_id, b.text]) : [])
const bodyWithBridges = sections.map(s => `## ${s.title}\n\n${bridges.get(s.id) ? `*${bridges.get(s.id)}*\n\n` : ''}${s.markdown}`).join('\n\n')
const esc = s => String(s || '').replace(/\|/g, '\\|').replace(/\n+/g, ' ')
const appendices = []
appendices.push(`## Appendix A. Claim table\n\n| ID | Claim | Status | Source type | Date | Source | Origin |\n|---|---|---|---|---|---|---|\n${claims.map(c => `| ${c.id} | ${esc(c.claim)} | ${c.status} | ${c.source_type} | ${esc(c.published || '')} | [${c.sid}](${c.url}) | ${esc(c.origin.ref)} |`).join('\n')}`)
appendices.push(`## Appendix B. Sources\n\n${finalSources.map(s => `${s.n}. **${esc(s.title)}** — ${s.platform}${s.published ? `, ${esc(s.published)}` : ''} — ${s.url} — ${s.source_type}; cited by ${s.claim_ids.length} claim(s)`).join('\n')}`)
const voiceGroups = {}
for (const v of voices) (voiceGroups[v.platform || 'other'] = voiceGroups[v.platform || 'other'] || []).push(v)
appendices.push(`## Appendix C. Community voices\n\n${Object.entries(voiceGroups).map(([p, vs]) => `### ${p}\n\n${vs.map(v => `> ${esc(v.quote)}\n> — ${esc(v.author)}, ${esc(v.date || 'undated')}, ${v.stance}${v.upvotes ? `, ${esc(v.upvotes)} votes` : ''}; credibility: ${esc(v.credibility)} — ${v.url}`).join('\n\n')}`).join('\n\n') || '_none recorded_'}`)
appendices.push(`## Appendix D. Timeline\n\n${timeline.slice().sort((a, b) => String(a.date).localeCompare(String(b.date))).map(t => `- **${esc(t.date)}** — ${esc(t.event)}${t.url ? ` ([source](${t.url}))` : ''}`).join('\n') || '_none recorded_'}`)
appendices.push(`## Appendix E. Numbers\n\n| What | Value | Who | Date | Challenged | Source |\n|---|---|---|---|---|---|\n${numbers.map(n => `| ${esc(n.what)} | ${esc(n.value)} | ${esc(n.who || '')} | ${esc(n.date || '')} | ${n.challenged ? 'yes' : ''} | ${n.url} |`).join('\n')}`)
if (front) appendices.push(`## Appendix F. Glossary\n\n${front.glossary}`)
appendices.push(`## Appendix G. Entity dossiers\n\n${dossiers.map(d => `### ${d.name} (${d.entity_type}, swarm ${d.swarm_id}, depth ${d.depth})\n\n${d.what_it_is}\n\n**Consensus:**${d.consensus_claims.map(x => `\n- ${x}`).join('')}\n\n**Dissent:**${d.dissent.map(x => `\n- ${x}`).join('') || ' none recorded'}\n\n**Primary sources:** ${(d.primary_sources || []).join('; ') || 'none'}\n\n**Credibility:** ${d.credibility_assessment}\n\n**Relation to the question:** ${d.relation_to_question}\n\n**Open questions:**${d.open_questions.map(x => `\n- ${x}`).join('') || ' none'}`).join('\n\n') || '_no swarms were run_'}`)
appendices.push(`## Appendix H. Dissent register\n\n### Contradictions noted by researchers\n${entries.flatMap(e => e.contradictions.map(c => `- (${e.id}) ${esc(c)}`)).join('\n') || '- none'}\n\n### Contested, refuted and outdated claims\n${claims.filter(c => ['contested', 'refuted', 'outdated'].includes(c.status)).map(c => `- **${c.id}** [${c.status}] ${esc(c.claim)} — ${c.notes.map(esc).join(' / ')}`).join('\n') || '- none'}\n\n### Claims whose citation failed verification\n${claims.filter(c => c.status === 'citation_failed').map(c => `- **${c.id}** ${esc(c.claim)} — ${c.url} — ${c.notes.map(esc).join(' / ')}`).join('\n') || '- none'}`)
appendices.push(`## Appendix I. Unexplored leads\n\n${parked.map(l => `- **${esc(l.name)}** (${l.entity_type}, score ${l.prescore}, round ${l.round}) — ${esc(l.lead)} — parked: ${esc(l.why_parked)}${l.canonical_url ? ` — ${l.canonical_url}` : ''}`).join('\n') || '- none'}\n\n### Unanswered items\n${entries.flatMap(e => e.unanswered.map(u => `- (${e.id}) ${esc(u)}`)).join('\n') || '- none'}\n\n### Proposed but unresearched sub-questions\n${unresearched.map(u => `- ${esc(u)}`).join('\n') || '- none'}`)
const finalStats = stats()
appendices.push(`## Appendix J. Methodology and review log\n\n- Rounds: ${round} (min ${MIN_ROUNDS}, max ${MAX_ROUNDS}); depth mode: ${MAX ? 'max' : 'standard'}\n- Sub-questions researched: ${entries.filter(e => e.kind === 'subquestion').length}, each by three researchers (primary, community, contrarian) plus second passes where thin\n- Deep-dive swarms: ${swarmed.size} (${[...swarmed.values()].map(v => `${v.name} [${v.entity_type}, depth ${v.depth}, ${v.agents} agents]`).join('; ') || 'none'})\n- Follow-ups: ${entries.filter(e => e.kind === 'followup').length}\n- Claims: ${claims.length} total; ${Object.entries(finalStats).map(([k, v]) => `${k} ${v}`).join(', ')}\n- Sources: ${sources.size}; community voices: ${voices.length}; numbers: ${numbers.length}; timeline entries: ${timeline.length}\n- Verification: every claim quote-checked against its page; key and community claims then judged by ${SKEPTICS}-skeptic panels (${JUDGE_CHUNK} claims per panel) with an adjudicator on split votes; other claims are source-checked only\n- Agents used: ${used}${downgrades.length ? `; budget downgrades: ${downgrades.join('; ')}` : ''}\n- Review passes: ${reviewLog.length}\n\n| Pass | Issues raised | Accepted | Blocking | Rejected | By lens |\n|---|---|---|---|---|---|\n${reviewLog.map(r => `| ${r.pass} | ${r.raised} | ${r.accepted} | ${r.blocking} | ${r.rejected} | ${esc(Object.entries(r.by_lens).map(([k, v]) => `${k} ${v}`).join(', '))} |`).join('\n')}\n${lastBlocking ? `\n**Known limitations:** ${lastBlocking} blocking review issue(s) remained when the review budget was exhausted; see the last review pass.` : ''}`)

// resolve [S#] tokens -> numbered links
const byToken = new Map(finalSources.map(s => [s.id, s]))
const resolve = text => text.replace(/\[(S\d+)\]/g, (m, t) => { const s = byToken.get(t); return s ? `[${s.n}](${s.url})` : m })
const toc = `## Contents\n\n${['Executive summary', 'How to read this report', ...sections.map(s => s.title), ...appendices.map(a => a.split('\n')[0].replace(/^## /, ''))].map((t, i) => `${i + 1}. ${t}`).join('\n')}`
const report = resolve(`# ${outline.title}\n\n_Research completed ${TODAY}. ${claims.length} claims from ${sources.size} sources; ${swarmed.size} deep-dive swarms; ${reviewLog.length} review passes._\n\n${toc}\n\n${frontText}${bodyWithBridges}\n\n# Appendices\n\n${appendices.join('\n\n')}`)

const wordsBody = sections.reduce((n, s) => n + s.word_count, 0) + (front ? wc(front.executive_summary) + wc(front.how_to_read) : 0)
return {
  report,
  title: outline.title,
  words_body: wordsBody,
  words_total: wc(report),
  outline: sections.map(s => ({ id: s.id, title: s.title, words: s.word_count })),
  rounds: round,
  subquestions: entries.filter(e => e.kind === 'subquestion').map(e => e.question),
  swarms: [...swarmed.values()],
  claims: { total: claims.length, ...finalStats },
  sources: sources.size,
  voices: voices.length,
  review_passes: reviewLog.length,
  review_log: reviewLog,
  blocking_issues_remaining: lastBlocking,
  agents_used: used,
  governor_downgrades: downgrades,
  unresearched_subquestions: unresearched,
  parked_leads: parked.length,
}
