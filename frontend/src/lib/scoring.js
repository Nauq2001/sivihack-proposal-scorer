/** Criteria, weights and the overall score. Shared with the backend contract:
 *  see docs/api/review-contract.md. */

export const CRITERIA = [
  { id: 'pu', name: 'Problem understanding', description: 'Reflects the client’s actual stated problem and goals, not a generic pitch.' },
  { id: 'scope', name: 'Scope & deliverables', description: 'Deliverables are specific; clear what is and isn’t included.' },
  { id: 'price', name: 'Pricing clarity', description: 'Price stated, broken down, easy to follow.' },
  { id: 'time', name: 'Timeline clarity', description: 'Concrete milestones and dates.' },
  { id: 'comp', name: 'Completeness vs. RFP', description: 'Every explicit RFP requirement is addressed.' },
  { id: 'risk', name: 'Risks & assumptions', description: 'Dependencies and risks are flagged, not hidden.' },
]

export const LEVELS = [
  ['low', 'Low'],
  ['medium', 'Medium'],
  ['high', 'High'],
]
export const LEVEL_WEIGHT = { low: 1, medium: 2, high: 3 }
export const LEVEL_NAME = { low: 'Low', medium: 'Medium', high: 'High' }

export const DEFAULT_LEVELS = Object.fromEntries(CRITERIA.map((c) => [c.id, 'medium']))

/** Weighted average of the per-criterion scores the backend returned. Kept on
 *  the client so changing a weight updates the score without a new request. */
export function overallScore(criteria, levels) {
  const scored = criteria.filter((c) => typeof c.score === 'number')
  const total = scored.reduce((sum, c) => sum + LEVEL_WEIGHT[levels[c.id] || 'medium'], 0)
  if (!total) return 0
  return scored.reduce((sum, c) => sum + c.score * LEVEL_WEIGHT[levels[c.id] || 'medium'], 0) / total
}

export function verdictOf(score) {
  if (score < 2.5) return ['bad', 'Not ready to send']
  if (score < 4) return ['warn', 'Revise before sending']
  return ['good', 'Ready after minor edits']
}

export function scoreTone(score) {
  return score <= 2 ? 'bad' : score < 4 ? 'warn' : 'good'
}

export function weightNote(levels, suggested) {
  if (suggested && CRITERIA.every((c) => levels[c.id] === suggested[c.id])) return 'Weighted for this client’s priorities'
  if (CRITERIA.every((c) => levels[c.id] === 'medium')) return 'All criteria at Medium'
  return 'Custom weights'
}

export function criteriaPayload(levels) {
  return CRITERIA.map((c) => ({ id: c.id, name: c.name, description: c.description, weight: levels[c.id] || 'medium' }))
}

export const STATUS_GLYPH = { met: '✓', partial: '~', missing: '✕', conflict: '≠' }
export const STATUS_LABEL = { met: 'Addressed', partial: 'Vague or partial', missing: 'Missing', conflict: 'Contradicts RFP' }
