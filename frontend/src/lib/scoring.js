/** Đọc kết quả từ backend. Hợp đồng: docs/api/review-contract.md
 *
 *  Người dùng không chỉnh tiêu chí nữa: trọng số do RFP Analyst đề xuất và đi
 *  thẳng vào chấm điểm, nên frontend chỉ hiển thị chứ không tính lại. */

export const RECOMMENDATION = {
  ready: { tone: 'good', label: 'Ready to send', note: 'Minor edits at most' },
  revise: { tone: 'warn', label: 'Revise before sending', note: 'The gaps are fixable' },
  do_not_accept_as_written: { tone: 'bad', label: 'Do not send as written', note: 'A stated constraint is broken' },
}

export const STATUS = {
  met: { glyph: '✓', label: 'Addressed', tone: 'good' },
  partial: { glyph: '~', label: 'Vague or partial', tone: 'warn' },
  missing: { glyph: '✕', label: 'Missing', tone: 'bad' },
  contradicted: { glyph: '≠', label: 'Contradicts the RFP', tone: 'conflict' },
  unsubstantiated: { glyph: '!', label: 'Promised without backing', tone: 'conflict' },
}

export const KIND = {
  strength: 'Strength',
  missing: 'Missing',
  vague: 'Vague',
  contradiction: 'Contradiction',
  unsupported_promise: 'Unsupported promise',
  risk_disclosure: 'Risk disclosure',
}

export const SEVERITY = {
  critical: { rank: 0, label: 'Critical', tone: 'bad' },
  major: { rank: 1, label: 'Major', tone: 'bad' },
  minor: { rank: 2, label: 'Minor', tone: 'warn' },
  info: { rank: 3, label: 'Note', tone: 'good' },
}

export const ORIGIN = {
  base: 'Base rubric',
  rfp_explicit: 'Stated in the RFP',
  ai_inferred: 'Read from the RFP',
  user: 'Added by the team',
}

export function scoreTone(score) {
  return score <= 2 ? 'bad' : score < 4 ? 'warn' : 'good'
}

/** Màu theo mức cần xử lý trước: điểm thấp trên tiêu chí nặng thì đỏ. */
export function attentionTone(score, weight) {
  if (typeof score !== 'number') return null
  const drag = (5 - score) * (weight || 1)
  if (drag >= 6) return 'bad'
  if (drag >= 3) return 'warn'
  return 'good'
}

export function sortedFindings(findings) {
  return [...findings].sort((a, b) => (SEVERITY[a.severity]?.rank ?? 9) - (SEVERITY[b.severity]?.rank ?? 9))
}

export function countBy(items, key) {
  return items.reduce((acc, item) => {
    acc[item[key]] = (acc[item[key]] || 0) + 1
    return acc
  }, {})
}

export const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches
