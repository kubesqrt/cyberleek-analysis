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

// args: { question: string, objective?: string, context?: string, examples?: string[], today?: string, depth?: 'standard' | 'max' }
const Q = typeof args === 'string' ? { question: args } : (args || {})
if (!Q.question) throw new Error('deep-research: pass args.question')
const MAX = Q.depth === 'max'
const SKEPTICS = MAX ? 3 : 2
const MAX_ROUNDS = MAX ? 6 : 4
const OBJECTIVE = Q.objective || ''
const TODAY = Q.today || 'unknown (check the date of every source)'
const EXAMPLES = Array.isArray(Q.examples) ? Q.examples.filter(Boolean) : []
const EXAMPLES_NOTE = EXAMPLES.length ? `ILLUSTRATIVE EXAMPLES (given by the user to show what they mean; they are NOT the research target):
${EXAMPLES.map(e => `- ${e}`).join('\n')}
Research the general category these examples belong to. An example may appear as one data point among many, never as the focus. Look for other instances, the full range of variants, and cases that break the pattern.` : ''

const TOOLS_NOTE = `Tools: first run ToolSearch with query "select:WebSearch,WebFetch" to load web tools.
Use WebSearch mode "extended" for anything niche, recent, numeric or contested; "standard" for quick lookups.
Open and read the actual pages with WebFetch — never cite a page from its search snippet alone.
Forums and communities: search them deliberately (Reddit, Hacker News, Stack Exchange, GitHub issues/discussions, specialist forums, review sites, public Discord/Discourse archives, YouTube comments, niche blogs). Use queries like "site:reddit.com <topic>". If a Reddit page won't load, try old.reddit.com or append ".json" to the thread URL.
Today's date: ${TODAY}.`

const SOURCE_RULES = `Source rules:
- Prefer primary sources: official docs, filings, datasets, papers, statutes, standards, the original announcement, the author's own words.
- Treat SEO blogs, content farms, AI-generated summaries and undated pages as weak; use them only to find primary sources.
- Record the publication date of every source. Flag anything that may be outdated.
- Every claim needs a URL plus a short verbatim quote that supports it. No quote, no claim.
- Separate fact from opinion/forecast. Note when sources disagree instead of picking one silently.
- Forum/community posts are source_type "community": treat them as experience reports and leads, not established fact. They count as strong only when several independent users report the same thing.
- If you cannot find something, say so. Never fill gaps from memory.`

const TRAIL_RULES = `Follow the trail, like a curious human researcher:
- Don't just run your starting queries and stop. When a source mentions something unexpected (a tool, person, company, term, workaround, linked thread, cited study, or a "you should look at Y instead"), chase it: open it, search it, and see where it leads.
- Hop between source types: forum post → the thing it links → the official docs → another community's take on it → back again.
- Notice the vocabulary insiders use and search with it; it unlocks better results than the outsider's phrasing.
- Spend roughly 60% of your effort on your sub-question and 40% on promising trails.
- Report the trails you didn't have time to finish as "leads", with a note on why each looks promising. Other researchers will pick them up.`

const OBJECTIVE_NOTE = OBJECTIVE ? `USER'S OBJECTIVE (what they want to achieve with this research): ${OBJECTIVE}
Keep this in mind: favour findings that are actionable for this objective, and look for options, approaches, tools, pitfalls and tips that real people report.` : ''

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
    source_type: { type: 'string', enum: ['primary', 'secondary', 'community', 'weak'] },
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
    leads: {
      type: 'array',
      description: 'promising trails found but not fully followed',
      items: {
        type: 'object',
        properties: {
          lead: { type: 'string' },
          why: { type: 'string' },
          where: { type: 'string', description: 'URL or place to start' },
        },
        required: ['lead', 'why'],
      },
    },
    sources_read: { type: 'integer' },
  },
  required: ['summary', 'claims', 'unanswered', 'leads'],
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
${OBJECTIVE_NOTE}
${EXAMPLES_NOTE}

${TOOLS_NOTE}
${EXAMPLES.length ? `
Anti-anchoring rules for the plan:
- At most ONE sub-question may be about the given example(s) specifically.
- Include a sub-question that maps the whole landscape: enumerate the other members/instances of the category, aiming for breadth.
- Include a sub-question on how instances differ from each other and on the counter-examples that don't fit the pattern.
- Search angles must use category-level terms, not only the example's name.
` : ''}
Do a few quick orienting searches first so the plan reflects the real landscape (terminology, key players, where the data lives).
Then break the question into ${MAX ? '8-14' : '6-10'} sub-questions that together fully answer it with no big overlaps.
Include sub-questions for: definitions/scope, the core facts, quantitative data, the strongest counter-evidence or opposing view, recent developments, and practical implications.
Include at least ${MAX ? 2 : 1} sub-question(s) dedicated to what practitioners and real users say in forums and communities (experiences, complaints, workarounds, hidden alternatives, insider knowledge).
Include at least one deliberately lateral sub-question: an adjacent field, an unconventional angle, or a "what would an expert in a different domain look at?" question.${OBJECTIVE ? '\nSince the user has an objective, include a sub-question that surveys the realistic options/approaches for achieving it.' : ''}
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
${EXAMPLES.length ? `Note: the user's example(s) (${EXAMPLES.join('; ')}) only illustrate the category. Unless your sub-question is about them, cover the broader set and don't spend your effort on them.\n` : ''}
${OBJECTIVE_NOTE}

${TOOLS_NOTE}

${SOURCE_RULES}

${TRAIL_RULES}

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
For community/forum claims (experience reports), "confirmed" means several independent users or a primary source report the same thing; a single anecdote is "unclear".

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
    const leads = (r.found.leads || []).map(l => `${l.lead} (${l.why}${l.where ? `; start: ${l.where}` : ''})`).join('; ')
    return `## ${r.sq.id}: ${r.sq.question}\n${r.found.summary}\nUnanswered: ${(r.found.unanswered || []).join('; ') || 'none'}\nKey claims not confirmed: ${refuted}\nOpen leads: ${leads || 'none'}`
  }).join('\n\n')
  const gaps = await agent(`You are the research director for an investigation into:
"${plan.restated_question}"
${OBJECTIVE_NOTE}

Findings so far:
${digest}

Already-researched sub-questions:
${[...seen].join('\n')}

What is still missing for a complete, trustworthy answer?${EXAMPLES.length ? ` First check for anchoring: is the research over-focused on the user's illustrative example(s) (${EXAMPLES.join('; ')})? If so, propose sub-questions that broaden coverage of the category.` : ''} Consider: unanswered items, key claims that failed verification, missing counter-evidence, missing quantitative data, missing recent developments, perspectives not represented.
Also look at the open leads the researchers found. Pick the most promising ones, especially surprising discoveries, insider tips, or alternatives nobody planned for, and turn them into sub-questions so the research follows where the evidence leads, not just the original plan. Connect dots across sub-questions: if two findings together suggest something new, investigate it.
Return only NEW sub-questions that would materially change or strengthen the answer (max ${MAX ? 8 : 5}). Mix gap-filling and lead-following. Set done=true if nothing material is missing.`,
    { phase: 'Gaps', label: `gaps:round${round}`, schema: GAPS, effort: 'high' })

  queue = (gaps && !gaps.done ? gaps.new_subquestions : [])
    .filter(sq => !seen.has(sq.question.toLowerCase()))
    .map(sq => ({ ...sq, id: `R${round + 1}-${sq.id}` }))
}
if (queue.length) log(`Stopped after ${MAX_ROUNDS} rounds with ${queue.length} gap(s) left unresearched: ${queue.map(q => q.question).join(' | ')}`)

// ---- Synthesize ----
phase('Synthesize')
const evidence = ledger.map(r => {
  const leads = (r.found.leads || []).map(l => `  - lead: ${l.lead} (${l.why})`).join('\n')
  const status = i => (r.verdicts.find(v => v.index === i) || {}).status || 'unverified (non-key)'
  const claims = r.found.claims.map((c, i) => `- [${status(i)}] [${c.source_type}, ${c.published || 'undated'}] ${c.claim} — ${c.url} — "${c.quote}"`).join('\n')
  const notes = r.verdicts.filter(v => v.status !== 'confirmed').map(v => `  - claim ${v.index} ${v.status}: ${v.notes.join(' / ')}`).join('\n')
  return `## ${r.sq.id}: ${r.sq.question}\n${r.found.summary}\n${claims}\n${notes ? `Fact-check notes:\n${notes}` : ''}\nContradictions: ${(r.found.contradictions || []).join('; ') || 'none'}\nUnanswered: ${(r.found.unanswered || []).join('; ') || 'none'}${leads ? `\nLeads:\n${leads}` : ''}`
}).join('\n\n')

const report = await agent(`Write the final research report answering:
"${plan.restated_question}"
${Q.context ? `User context: ${Q.context}` : ''}
${OBJECTIVE_NOTE}
${EXAMPLES.length ? `The user's example(s) (${EXAMPLES.join('; ')}) were illustrations. Answer at the category level, and mention the example only where it is a useful data point.\n` : ''}
Use ONLY the evidence ledger below. Do not add facts from memory.
- Build on claims marked confirmed. Claims marked refuted or outdated must not be stated as true (mention them only as debunked/outdated if relevant). Contested/unverified claims must be labelled as such.
- Cite inline as markdown links [n](url) and finish with a numbered source list (title/site, date, url).
- Label community/forum evidence as such ("users on r/xyz report…") and say how widespread it seems.

Structure:
1. Bottom line (5-10 sentences, the direct answer, with overall confidence)
2. Key findings (each with citations and a confidence tag)
${OBJECTIVE ? '2b. Recommendations for the objective: ranked, concrete suggestions/options with pros, cons, cost/effort, risks and the evidence behind each; then suggested next steps\n' : ''}2c. Discovery trail: the surprising things found along the way and how one lead led to another
3. Detailed analysis (organised by theme, not by sub-question)
4. Where the evidence disagrees, and why
5. What is still unknown or could not be verified, plus open leads worth pursuing next
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
