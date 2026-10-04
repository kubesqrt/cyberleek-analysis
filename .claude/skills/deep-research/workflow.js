export const meta = {
  name: 'deep-research',
  description: 'Multi-agent deep research: plan, parallel web research, adversarial fact-check, gap-fill rounds, cited report',
  whenToUse: 'In-depth research on any question where accuracy and source coverage matter',
  phases: [
    { title: 'Plan', detail: 'decompose the question into sub-questions and search angles' },
    { title: 'Research', detail: 'one researcher per sub-question, primary sources, claim ledger' },
    { title: 'Verify', detail: 'independent skeptics try to refute each key claim' },
    { title: 'Gaps', detail: 'completeness critic finds what is missing; loop until dry' },
    { title: 'Synthesize', detail: 'write the cited report' },
  ],
}

// args: { question: string, context?: string, today?: string, depth?: 'standard' | 'max' }
const Q = typeof args === 'string' ? { question: args } : (args || {})
if (!Q.question) throw new Error('deep-research: pass args.question')
const MAX = Q.depth === 'max'
const SKEPTICS = MAX ? 3 : 2
const MAX_ROUNDS = MAX ? 4 : 3
const TODAY = Q.today || 'unknown (check the date of every source)'

const TOOLS_NOTE = `Tools: first run ToolSearch with query "select:WebSearch,WebFetch" to load web tools.
Use WebSearch mode "extended" for anything niche, recent, numeric or contested; "standard" for quick lookups.
Open and read the actual pages with WebFetch — never cite a page from its search snippet alone.
Today's date: ${TODAY}.`

const SOURCE_RULES = `Source rules:
- Prefer primary sources: official docs, filings, datasets, papers, statutes, standards, the original announcement, the author's own words.
- Treat SEO blogs, content farms, AI-generated summaries and undated pages as weak; use them only to find primary sources.
- Record the publication date of every source. Flag anything that may be outdated.
- Every claim needs a URL plus a short verbatim quote that supports it. No quote, no claim.
- Separate fact from opinion/forecast. Note when sources disagree instead of picking one silently.
- If you cannot find something, say so. Never fill gaps from memory.`

const PLAN = {
  type: 'object',
  properties: {
    restated_question: { type: 'string' },
    assumptions: { type: 'array', items: { type: 'string' } },
    subquestions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          question: { type: 'string' },
          why: { type: 'string' },
          search_angles: { type: 'array', items: { type: 'string' } },
        },
        required: ['id', 'question', 'search_angles'],
      },
    },
  },
  required: ['restated_question', 'subquestions'],
}

const CLAIM = {
  type: 'object',
  properties: {
    claim: { type: 'string' },
    url: { type: 'string' },
    quote: { type: 'string' },
    source_type: { type: 'string', enum: ['primary', 'secondary', 'weak'] },
    published: { type: 'string' },
    key: { type: 'boolean', description: 'true if the final answer depends on this claim' },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['claim', 'url', 'quote', 'source_type', 'key', 'confidence'],
}

const FINDINGS = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    claims: { type: 'array', items: CLAIM },
    contradictions: { type: 'array', items: { type: 'string' } },
    unanswered: { type: 'array', items: { type: 'string' } },
    sources_read: { type: 'integer' },
  },
  required: ['summary', 'claims', 'unanswered'],
}

const VERDICTS = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          index: { type: 'integer' },
          status: { type: 'string', enum: ['confirmed', 'refuted', 'unclear', 'outdated'] },
          evidence_url: { type: 'string' },
          note: { type: 'string' },
        },
        required: ['index', 'status', 'note'],
      },
    },
  },
  required: ['verdicts'],
}

const GAPS = {
  type: 'object',
  properties: {
    done: { type: 'boolean' },
    new_subquestions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          question: { type: 'string' },
          why: { type: 'string' },
          search_angles: { type: 'array', items: { type: 'string' } },
        },
        required: ['id', 'question', 'search_angles'],
      },
    },
  },
  required: ['done', 'new_subquestions'],
}

// ---- Plan ----
phase('Plan')
const plan = await agent(`You are planning a deep research project.

QUESTION: ${Q.question}
${Q.context ? `CONTEXT FROM THE USER: ${Q.context}` : ''}

${TOOLS_NOTE}

Do a few quick orienting searches first so the plan reflects the real landscape (terminology, key players, where the data lives).
Then break the question into ${MAX ? '8-14' : '6-10'} sub-questions that together fully answer it with no big overlaps.
Include sub-questions for: definitions/scope, the core facts, quantitative data, the strongest counter-evidence or opposing view, recent developments, and practical implications.
For each, list 3-5 concrete search angles (specific queries, specific sites/databases/registries, specific document types).`,
  { phase: 'Plan', schema: PLAN, effort: 'high' })

if (!plan) throw new Error('planning agent failed')
log(`Plan: ${plan.subquestions.length} sub-questions`)

// ---- Research + Verify, pipelined per sub-question ----
const research = sq => agent(`You are one researcher on a team answering:
"${plan.restated_question}"

YOUR SUB-QUESTION (${sq.id}): ${sq.question}
${sq.why ? `Why it matters: ${sq.why}` : ''}
Starting angles: ${sq.search_angles.join(' | ')}

${TOOLS_NOTE}

${SOURCE_RULES}

Go deep: run many searches with varied phrasing, follow citations to the original source, and read at least ${MAX ? 10 : 6} distinct sources in full.
Return every useful claim with its evidence. Mark key=true on claims the final answer will depend on.`,
  { phase: 'Research', label: `research:${sq.id}`, schema: FINDINGS })

const verify = async (found, sq) => {
  if (!found) return null
  const keyClaims = found.claims.map((c, i) => ({ ...c, index: i })).filter(c => c.key)
  if (!keyClaims.length) return { sq, found, verdicts: [] }
  const list = keyClaims.map(c => `[${c.index}] ${c.claim}\n    source: ${c.url} (${c.published || 'undated'})\n    quote: "${c.quote}"`).join('\n')
  const votes = await parallel(Array.from({ length: SKEPTICS }, (_, n) => () => agent(`You are fact-checker #${n + 1}. Your job is to REFUTE the claims below, not to agree with them.

${TOOLS_NOTE}

For each claim:
1. Open the cited URL and check the quote actually exists and actually supports the claim (not taken out of context).
2. Search for INDEPENDENT sources (not copies of the same original) that confirm or contradict it.
3. Check whether it is outdated as of today.
Mark "confirmed" only with independent support. If unsure, mark "unclear".

CLAIMS:
${list}`, { phase: 'Verify', label: `verify:${sq.id}#${n + 1}`, schema: VERDICTS })))

  const verdicts = keyClaims.map(c => {
    const vs = votes.filter(Boolean).flatMap(v => v.verdicts).filter(v => v.index === c.index)
    const count = s => vs.filter(v => v.status === s).length
    const status = count('refuted') > vs.length / 2 ? 'refuted'
      : count('outdated') > vs.length / 2 ? 'outdated'
      : count('confirmed') > vs.length / 2 ? 'confirmed' : 'contested'
    return { index: c.index, status, notes: vs.map(v => `${v.status}: ${v.note}${v.evidence_url ? ` (${v.evidence_url})` : ''}`) }
  })
  return { sq, found, verdicts }
}

const ledger = []
const seen = new Set()
let queue = plan.subquestions
let round = 0

while (queue.length && round < MAX_ROUNDS) {
  round++
  queue.forEach(sq => seen.add(sq.question.toLowerCase()))
  log(`Round ${round}: researching ${queue.length} sub-questions`)
  const results = await pipeline(queue, research, verify)
  ledger.push(...results.filter(Boolean))
  const failed = results.filter(r => !r).length
  if (failed) log(`${failed} sub-question(s) failed in round ${round}`)

  // ---- Gaps ----
  const digest = ledger.map(r => {
    const refuted = r.verdicts.filter(v => v.status !== 'confirmed').length
    return `## ${r.sq.id}: ${r.sq.question}\n${r.found.summary}\nUnanswered: ${(r.found.unanswered || []).join('; ') || 'none'}\nKey claims not confirmed: ${refuted}`
  }).join('\n\n')
  const gaps = await agent(`You are the completeness critic for research on:
"${plan.restated_question}"

Findings so far:
${digest}

Already-researched sub-questions:
${[...seen].join('\n')}

What is still missing for a complete, trustworthy answer? Consider: unanswered items, key claims that failed verification, missing counter-evidence, missing quantitative data, missing recent developments, perspectives not represented.
Return only NEW sub-questions that would materially change or strengthen the answer (max ${MAX ? 6 : 4}). Set done=true if nothing material is missing.`,
    { phase: 'Gaps', label: `gaps:round${round}`, schema: GAPS, effort: 'high' })

  queue = (gaps && !gaps.done ? gaps.new_subquestions : [])
    .filter(sq => !seen.has(sq.question.toLowerCase()))
    .map(sq => ({ ...sq, id: `R${round + 1}-${sq.id}` }))
}
if (queue.length) log(`Stopped after ${MAX_ROUNDS} rounds with ${queue.length} gap(s) left unresearched: ${queue.map(q => q.question).join(' | ')}`)

// ---- Synthesize ----
phase('Synthesize')
const evidence = ledger.map(r => {
  const status = i => (r.verdicts.find(v => v.index === i) || {}).status || 'unverified (non-key)'
  const claims = r.found.claims.map((c, i) => `- [${status(i)}] [${c.source_type}, ${c.published || 'undated'}] ${c.claim} — ${c.url} — "${c.quote}"`).join('\n')
  const notes = r.verdicts.filter(v => v.status !== 'confirmed').map(v => `  - claim ${v.index} ${v.status}: ${v.notes.join(' / ')}`).join('\n')
  return `## ${r.sq.id}: ${r.sq.question}\n${r.found.summary}\n${claims}\n${notes ? `Fact-check notes:\n${notes}` : ''}\nContradictions: ${(r.found.contradictions || []).join('; ') || 'none'}\nUnanswered: ${(r.found.unanswered || []).join('; ') || 'none'}`
}).join('\n\n')

const report = await agent(`Write the final research report answering:
"${plan.restated_question}"
${Q.context ? `User context: ${Q.context}` : ''}

Use ONLY the evidence ledger below. Do not add facts from memory.
- Build on claims marked confirmed. Claims marked refuted or outdated must not be stated as true (mention them only as debunked/outdated if relevant). Contested/unverified claims must be labelled as such.
- Cite inline as markdown links [n](url) and finish with a numbered source list (title/site, date, url).

Structure:
1. Bottom line (5-10 sentences, the direct answer, with overall confidence)
2. Key findings (each with citations and a confidence tag)
3. Detailed analysis (organised by theme, not by sub-question)
4. Where the evidence disagrees, and why
5. What is still unknown or could not be verified
6. Sources

EVIDENCE LEDGER:
${evidence}`, { phase: 'Synthesize', label: 'write-report', effort: 'high' })

return {
  report,
  rounds: round,
  subquestions: ledger.map(r => r.sq.question),
  claims_total: ledger.reduce((n, r) => n + r.found.claims.length, 0),
  key_claims: ledger.flatMap(r => r.verdicts).length,
  key_claims_confirmed: ledger.flatMap(r => r.verdicts).filter(v => v.status === 'confirmed').length,
  unresearched_gaps: queue.map(q => q.question),
}
