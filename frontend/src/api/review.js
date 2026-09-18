/** Calls the scoring service. Contract: docs/api/review-contract.md */

export class ReviewError extends Error {
  constructor(message, { offline = false } = {}) {
    super(message)
    this.name = 'ReviewError'
    this.offline = offline // true when the service isn't reachable at all
  }
}

const MIN_MS = 1800 // the progress steps need a moment to be readable

export async function reviewProposal({ rfp, proposal }) {
  const started = Date.now()
  let res
  try {
    res = await fetch('/api/review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rfp, proposal }),
    })
  } catch (err) {
    throw new ReviewError('The scoring service is not reachable. Start the backend on port 8000.', { offline: true })
  }

  if (res.status === 404) throw new ReviewError('The backend is running but /api/review does not exist yet.', { offline: true })
  if (!res.ok) {
    const detail = await res.json().then((d) => d.detail || d.error).catch(() => null)
    throw new ReviewError(detail || `The scoring service returned ${res.status}.`)
  }

  const data = await res.json()
  const wait = MIN_MS - (Date.now() - started)
  if (wait > 0) await new Promise((r) => setTimeout(r, wait))
  return data
}
