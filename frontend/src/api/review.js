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

/** Duoi file backend chuyen duoc sang Markdown (/v1/markitdown/convert).
 *  Giu dung danh sach trong app/v1/endpoints/MarkitDown/router.py. */
export const CONVERTIBLE = [
  '.pdf', '.pptx', '.docx', '.xlsx', '.xls', '.html', '.htm',
  '.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tif', '.tiff',
]

/** File nao doc thang duoc bang FileReader, khong can qua backend. */
export const PLAIN_TEXT = ['.md', '.markdown', '.txt', '.text', '.csv', '.json']

export const extensionOf = (name) => {
  const at = String(name).lastIndexOf('.')
  return at === -1 ? '' : String(name).slice(at).toLowerCase()
}

/** Anh/PDF/Office -> Markdown. Backend goi MarkItDown, anh thi OCR qua Gemini. */
export async function convertFile(file) {
  const body = new FormData()
  body.append('file', file)
  let res
  try {
    res = await fetch('/v1/markitdown/convert', { method: 'POST', body })
  } catch {
    throw new ReviewError('The conversion service is not reachable. Start the backend on port 8000.', { offline: true })
  }
  if (res.status === 404) {
    throw new ReviewError('The backend is running but the file converter is not mounted.', { offline: true })
  }
  if (!res.ok) {
    const detail = await res.json().then((d) => d.detail || d.error).catch(() => null)
    throw new ReviewError(detail || `Reading ${file.name} failed with ${res.status}.`)
  }
  const data = await res.json()
  return String(data.markdown || '')
}

/** RFP Analyst: doc RFP ra yeu cau va tieu chi kem trong so. */
export const analyseRfp = ({ rfp }) => post('/api/analyze-rfp', { raw_rfp_text: rfp.text }, 'Reading the RFP')

/** Chot tieu chi. Chay mot lan, ngay truoc khi cham — khong phai moi lan nguoi
 *  dung them mot tieu chi. Backend goi resolver cua agent o day. */
export const confirmCriteria = ({ rfp, rfp_analysis, criteria }) =>
  post('/api/confirm-criteria', { rfp_analysis, raw_rfp_text: rfp.text, criteria }, 'Confirming the criteria')

/** Scoring Agent: cham proposal theo danh sach tieu chi da chot. */
export const scoreProposal = ({ rfp, proposal, rfp_analysis, confirmed_criteria }) =>
  post('/api/score', {
    rfp_analysis,
    raw_rfp_text: rfp.text,
    raw_proposal_text: proposal.text,
    confirmed_criteria,
  }, 'Scoring the proposal')
