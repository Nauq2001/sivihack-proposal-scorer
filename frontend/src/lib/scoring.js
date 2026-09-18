/** Criteria priorities and the overall score.
 *  Shared with the backend contract: see docs/api/review-contract.md */

/** How much a criterion pulls on the overall score. `weight` is the multiplier;
 *  the interface shows the note, never the number. */
export const PRIORITIES = [
  { id: 'high', label: 'High', weight: 3, hint: 'Pulls the score hardest. A gap here can lose the deal.' },
  { id: 'medium', label: 'Medium', weight: 2, hint: 'Weighs on the decision, but rarely decides it alone.' },
  { id: 'low', label: 'Low', weight: 1, hint: 'Worth getting right, moves the score a little.' },
  { id: 'skip', label: 'Don’t score', weight: 0, hint: 'Still reviewed and reported, left out of the number.' },
]

export const PRIORITY_IDS = PRIORITIES.map((p) => p.id)
export const PRIORITY_WEIGHT = Object.fromEntries(PRIORITIES.map((p) => [p.id, p.weight]))
export const PRIORITY_LABEL = Object.fromEntries(PRIORITIES.map((p) => [p.id, p.label]))

/** Weighted average of the scores the backend returned. Kept on the client so
 *  moving a card updates the score without a new request. */
export function overallScore(criteria, scoreById) {
  const counted = criteria.filter((c) => PRIORITY_WEIGHT[c.priority] > 0 && typeof scoreById[c.id]?.score === 'number')
  const total = counted.reduce((sum, c) => sum + PRIORITY_WEIGHT[c.priority], 0)
  if (!total) return { score: 0, counted: [] }
  const score = counted.reduce((sum, c) => sum + scoreById[c.id].score * PRIORITY_WEIGHT[c.priority], 0) / total
  return { score, counted }
}

export function verdictOf(score) {
  if (score < 2.5) return ['bad', 'Not ready to send']
  if (score < 4) return ['warn', 'Revise before sending']
  return ['good', 'Ready after minor edits']
}

export function scoreTone(score) {
  return score <= 2 ? 'bad' : score < 4 ? 'warn' : 'good'
}

/** One colour rule for the whole app: red means deal with this first.
 *  On the criteria board that is the heaviest criterion; here it is the one
 *  dragging the score down hardest, which is the gap below 5 times the weight.
 *  A weak score on a deal-breaker outranks the same score on a minor criterion. */
export function attentionTone(score, priority) {
  const weight = PRIORITY_WEIGHT[priority] ?? 0
  if (!weight || typeof score !== 'number') return null
  const drag = (5 - score) * weight
  if (drag >= 6) return 'bad'
  if (drag >= 3) return 'warn'
  return 'good'
}

export function matchesSuggestion(criteria) {
  return criteria.every((c) => !c.suggested_priority || c.priority === c.suggested_priority)
}

export function weightNote(criteria) {
  if (matchesSuggestion(criteria)) return 'Weighted for this client’s priorities'
  return 'Weighted by you'
}

/** What goes to POST /api/review. */
export function criteriaPayload(criteria) {
  return criteria.map((c) => ({
    id: c.id,
    name: c.name,
    description: c.description,
    priority: c.priority,
    source: c.source,
  }))
}

export const STATUS_GLYPH = { met: '✓', partial: '~', missing: '✕', conflict: '≠' }
export const STATUS_LABEL = { met: 'Addressed', partial: 'Vague or partial', missing: 'Missing', conflict: 'Contradicts RFP' }
