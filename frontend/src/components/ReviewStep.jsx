import { useRef, useState } from 'react'
import { SAMPLES } from '../data/samples.js'
import { Citations } from './Citation.jsx'
import {
  PRIORITIES, PRIORITY_LABEL, PRIORITY_WEIGHT, STATUS_GLYPH, STATUS_LABEL,
  overallScore, scoreTone, verdictOf, weightNote,
} from '../lib/scoring.js'

function FixBox({ text }) {
  const [label, setLabel] = useState('Copy')
  const ref = useRef(null)
  if (!text) return null

  const select = () => {
    const range = document.createRange()
    range.selectNodeContents(ref.current)
    const sel = window.getSelection()
    sel.removeAllRanges()
    sel.addRange(range)
    setLabel('Selected, press ⌘C')
  }
  const copy = () => {
    const reset = () => setTimeout(() => setLabel('Copy'), 1800)
    try {
      navigator.clipboard.writeText(text).then(() => { setLabel('Copied'); reset() }, () => { select(); reset() })
    } catch {
      select(); reset()
    }
  }

  return (
    <div className="fix">
      <div className="fix-head">
        Suggested fix
        <button type="button" className="btn btn-quiet" onClick={copy}>{label}</button>
      </div>
      <p className="fix-text" ref={ref}>{text}</p>
    </div>
  )
}

function Pips({ score }) {
  return (
    <div className="pips" data-tone={scoreTone(score)} style={{ background: 'none' }} aria-label={`${score} out of 5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <i key={n} className={'pip' + (n <= score ? ' on' : '')} />
      ))}
      <b>{score}/5</b>
    </div>
  )
}

export default function ReviewStep({ result, criteria, sampleId, source, error, onSample, onRun, onGo }) {
  const [flash, setFlash] = useState(null)
  const byId = Object.fromEntries(result.criteria.map((c) => [c.id, c]))
  const { score } = overallScore(criteria, byId)
  const [tone, verdict] = verdictOf(score)
  // Board order: deal-breakers first, then down to the ones left out.
  const ordered = PRIORITIES.flatMap((p) => criteria.filter((c) => c.priority === p.id))

  const counts = { met: 0, partial: 0, missing: 0, conflict: 0 }
  result.requirements.forEach((r) => { counts[r.status] += 1 })

  const jump = (id) => {
    const el = document.getElementById('req-' + id)
    if (!el) return
    el.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' })
    setFlash(null)
    requestAnimationFrame(() => setFlash(id))
  }

  return (
    <section>
      <div className="review-bar">
        <label htmlFor="review-sample">Reviewing</label>
        <select className="field" id="review-sample" value={sampleId || ''} onChange={(e) => onSample(e.target.value)}>
          {!sampleId && <option value="">{result.meta.proposal_name}</option>}
          {SAMPLES.map((s) => (
            <option key={s.id} value={s.id}>{s.label}</option>
          ))}
        </select>
        <div className="actions">
          <button type="button" className="btn" onClick={() => onGo('criteria')}>Adjust criteria</button>
          <button type="button" className="btn" onClick={onRun}>Run again</button>
        </div>
      </div>

      {source === 'sample' && (
        <p className="notice" style={{ marginBottom: 16 }}>
          <strong>Stored sample result.</strong> {error || 'The scoring service is not connected.'} Showing the saved
          review for {result.meta.proposal_name}.
        </p>
      )}

      <section className="verdict" aria-label="Overall result">
        <div>
          <div className="score-big">{score.toFixed(1)}<small>/5</small></div>
          <div className="score-cap">{weightNote(criteria)}</div>
        </div>
        <div>
          <span className="pill" data-tone={tone}>{verdict}</span>
          <p className="summary">{result.overall.summary}</p>
        </div>
        <div className="strip-wrap">
          <div className="strip-title">
            <span>RFP requirements</span>
            <span className="legend">
              {Object.keys(counts).filter((k) => counts[k]).map((k) => (
                <span key={k}><i data-st={k} />{counts[k]} {STATUS_LABEL[k].toLowerCase()}</span>
              ))}
            </span>
          </div>
          <div className="strip">
            {result.requirements.map((r) => (
              <button
                type="button"
                className="cell"
                key={r.id}
                data-st={r.status}
                onClick={() => jump(r.id)}
                aria-label={`${r.name}: ${r.status_label}`}
              >
                <span className="g">{STATUS_GLYPH[r.status]}</span>
                <span className="l">{r.short_label}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="block">
        <div className="block-head">
          <h2>Requirements and fixes</h2>
          <p>In RFP order. Click a citation to see the source text.</p>
        </div>
        <div className="panel">
          {result.requirements.map((r) => (
            <article className={'req' + (flash === r.id ? ' flash' : '')} id={'req-' + r.id} key={r.id}>
              <span className="badge" data-st={r.status}>{STATUS_GLYPH[r.status]} {r.status_label}</span>
              <div>
                <h3>{r.name}</h3>
                <p className="ask">{r.ask}</p>
                <p className="finding">{r.finding}</p>
                <Citations items={[r.rfp_citation, ...r.citations]} />
                <FixBox text={r.suggested_fix} />
                {r.clarification && (
                  <div className="clarify">
                    <h4>Worth clarifying: {r.clarification.title}</h4>
                    <p>{r.clarification.text}</p>
                    <Citations items={r.clarification.citations} />
                    <FixBox text={r.clarification.suggested_fix} />
                  </div>
                )}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="block">
        <div className="block-head">
          <h2>Scores by criterion</h2>
          <p>Ordered by how much each one counts, set on the criteria board</p>
        </div>
        <div className="panel">
          {ordered.map((c) => {
            const s = byId[c.id]
            const counted = PRIORITY_WEIGHT[c.priority] > 0
            return (
              <div className="cr" key={c.id} data-off={!counted || !s}>
                <div className="cr-name">
                  <strong>{c.name}</strong>
                  <span className="lvl" data-prio={c.priority}>
                    <i className="card-dot" data-prio={c.priority} aria-hidden="true" />
                    {PRIORITY_LABEL[c.priority]}{counted ? '' : ' — not counted'}
                  </span>
                </div>
                {s ? <Pips score={s.score} /> : <div className="pips">{[1, 2, 3, 4, 5].map((n) => <i key={n} className="pip" />)}<b>–</b></div>}
                <div className="cr-body">
                  <p>{s ? s.comment : 'Added after this run. Run the review again to score it.'}</p>
                  {s && <Citations items={s.citations} />}
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {result.other_issues.length > 0 && (
        <section className="block">
          <div className="block-head">
            <h2>Other issues</h2>
            <p>Not tied to a single requirement</p>
          </div>
          <div className="panel">
            {result.other_issues.map((o) => (
              <article className="req" key={o.id}>
                <span className="badge" data-st={o.status}>{STATUS_GLYPH[o.status]} {o.label}</span>
                <div>
                  <h3>{o.title}</h3>
                  <p className="finding">{o.finding}</p>
                  <Citations items={o.citations} />
                  <FixBox text={o.suggested_fix} />
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </section>
  )
}
