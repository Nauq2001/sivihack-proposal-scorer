import { useEffect, useMemo, useRef } from 'react'
import { renderMarkdown, findBlocks } from '../lib/markdown.js'

const reduceMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

/** The RFP and the proposal side by side with the findings. A citation
 *  highlights the exact block it came from, so a reviewer can check a claim
 *  instead of trusting a number. */
export default function SourcePane({ rfp, proposal, tab, onTab, citation, docked, open, onClose }) {
  const bodyRef = useRef(null)
  const doc = tab === 'rfp' ? rfp : proposal
  const html = useMemo(() => renderMarkdown(doc.text), [doc.text])

  useEffect(() => {
    const body = bodyRef.current
    if (!body) return
    body.querySelectorAll('.hl').forEach((el) => el.classList.remove('hl'))
    if (!citation || citation.found === false) return
    const wanted = citation.source === 'rfp' ? 'rfp' : 'prop'
    if (wanted !== tab) return
    const hits = findBlocks(body, citation.quote)
    hits.forEach((el) => el.classList.add('hl'))
    if (hits[0]) {
      body.scrollTo({ top: Math.max(0, hits[0].offsetTop - body.clientHeight / 3), behavior: reduceMotion() ? 'auto' : 'smooth' })
    }
  }, [citation, html, tab])

  const notFound = citation && citation.found === false && tab === 'prop'

  return (
    <aside id="source" className={open && !docked ? 'open' : undefined} aria-label="Source documents">
      <div className="src-head">
        <button type="button" className="tab" role="tab" aria-selected={tab === 'rfp'} onClick={() => onTab('rfp')}>RFP</button>
        <button type="button" className="tab" role="tab" aria-selected={tab === 'prop'} onClick={() => onTab('prop')}>Proposal</button>
        <span className="file">{doc.name}</span>
        <button type="button" className="icon-btn close" onClick={onClose} aria-label="Close source">
          <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
            <path d="M2 2l10 10M12 2L2 12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          </svg>
        </button>
      </div>
      {notFound && (
        <div className="src-note" data-st="missing">
          No mention of {citation.searched_terms.join(', ')} anywhere in the proposal.
        </div>
      )}
      <div className="src-body" ref={bodyRef} dangerouslySetInnerHTML={{ __html: html }} />
    </aside>
  )
}
