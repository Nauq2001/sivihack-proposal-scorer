/** Hai buoc, dung voi hai agent trong AI/: RFP Analyst roi Scoring Agent.
 *  Hop dong: docs/api/review-contract.md */

export class ReviewError extends Error {
  constructor(message, { offline = false } = {}) {
    super(message)
    this.name = 'ReviewError'
    this.offline = offline
  }
}

async function post(path, body, what) {
  let res
  try {
    res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  } catch {
    throw new ReviewError('The scoring service is not reachable. Start the backend on port 8000.', { offline: true })
  }
  if (res.status === 404) throw new ReviewError(`The backend is running but ${path} does not exist yet.`, { offline: true })
  if (!res.ok) {
    const detail = await res.json().then((d) => d.detail || d.error).catch(() => null)
    throw new ReviewError(detail || `${what} failed with ${res.status}.`)
  }
  return res.json()
}

/** RFP Analyst: doc RFP ra yeu cau va tieu chi kem trong so. */
export const analyseRfp = ({ rfp }) => post('/api/analyze-rfp', { raw_rfp_text: rfp.text }, 'Reading the RFP')

/** Scoring Agent: cham proposal theo danh sach tieu chi da chot. */
export const scoreProposal = ({ rfp, proposal, rfp_analysis, confirmed_criteria }) =>
  post('/api/score', {
    rfp_analysis,
    raw_rfp_text: rfp.text,
    raw_proposal_text: proposal.text,
    confirmed_criteria,
  }, 'Scoring the proposal')

/** Nut "Send to Work": nguoi dung tu bam, khong tu dong sau /api/score.
 *  n8n tao ticket Jira roi bao vao Slack; tra ve { ticket_key, ticket_url }. */
export const createTicket = (scoring) => post('/api/create-ticket', scoring, 'Creating the ticket')
