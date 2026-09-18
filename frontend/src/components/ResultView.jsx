import { useEffect, useRef, useState } from 'react'
import { Citations, Citation } from './Citation.jsx'
import { SAMPLES } from '../data/samples.js'
import {
  KIND, ORIGIN, RECOMMENDATION, SEVERITY, STATUS,
  attentionTone, countBy, reducedMotion, scoreTone, sortedFindings,
} from '../lib/scoring.js'

/** Điểm đếm lên, để con số là thứ đập vào mắt trước tiên. */
function CountUp({ value }) {
  const [shown, setShown] = useState(reducedMotion() ? value : 0)
  useEffect(() => {
    if (reducedMotion()) { setShown(value); return }
    const start = performance.now()
    const duration = 700
    let frame
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration)
      setShown(value * (1 - Math.pow(1 - t, 3)))
      if (t < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [value])
  return <>{shown.toFixed(1)}</>
}

function Gauge({ score }) {
  return (
    <div className="gauge">
      <div className="gauge-track" role="img" aria-label={`${score.toFixed(1)} out of 5`}>
        <span className="zone" data-tone="bad" />
        <span className="zone" data-tone="warn" />
        <span className="zone" data-tone="good" />
        <span className="gauge-mark" style={{ left: `${Math.min(100, Math.max(0, (score / 5) * 100))}%` }} />
      </div>
      <div className="gauge-labels"><span>Do not send</span><span>Revise</span><span>Ready</span></div>
    </div>
  )
}

function Pips({ score }) {
  return (
    <span className="pips" data-tone={scoreTone(score)} aria-label={`${score} out of 5`}>
      {[1, 2, 3, 4, 5].map((n) => <i key={n} className={'pip' + (n <= score ? ' on' : '')} />)}
    </span>
  )
}

function FixBox({ text }) {
  const [label, setLabel] = useState('Copy')
  const ref = useRef(null)
  if (!text) return null
  const copy = () => {
    const reset = () => setTimeout(() => setLabel('Copy'), 1800)
    const select = () => {
      const range = document.createRange()
      range.selectNodeContents(ref.current)
      const sel = window.getSelection()
      sel.removeAllRanges()
      sel.addRange(range)
      setLabel('Selected, press ⌘C')
    }
    try {
      navigator.clipboard.writeText(text).then(() => { setLabel('Copied'); reset() }, () => { select(); reset() })
    } catch { select(); reset() }
  }
  return (
    <div className="fix">
      <div className="fix-head">Suggested wording<button type="button" className="btn btn-quiet" onClick={copy}>{label}</button></div>
      <p className="fix-text" ref={ref}>{text}</p>
    </div>
  )
}

export default function ResultView({ result, source, error, sampleId, onSample, onRestart }) {
  const [flash, setFlash] = useState(null)
  const { rfp_analysis: analysis, confirmed_criteria: criteria, evaluation: ev } = result

  const statuses = countBy(ev.requirements, 'status')
  const byId = Object.fromEntries(ev.requirements.map((r) => [r.id, r]))
  const reqMeta = Object.fromEntries(analysis.requirements.map((r) => [r.id, r]))
  const findings = sortedFindings(ev.findings)
  const rec = RECOMMENDATION[ev.recommendation] || RECOMMENDATION.revise

  const jump = (id) => {
    const el = document.getElementById('req-' + id)
    if (!el) return
    el.scrollIntoView({ behavior: reducedMotion() ? 'auto' : 'smooth', block: 'center' })
    setFlash(null)
    requestAnimationFrame(() => setFlash(id))
  }

  return (
    <div className="result-view">
      {source === 'sample' && (
        <p className="notice reveal">
          <strong>Stored sample result.</strong> {error || 'The scoring service is not connected.'} Showing the saved
          review for {result.meta.proposal_name}.
        </p>
      )}

      <section className="verdict reveal">
        <div className="verdict-score">
          <span className="pill" data-tone={rec.tone}>{rec.label}</span>
          <div className="score-big"><CountUp value={ev.overall_score} /><small>/5</small></div>
          <p className="score-note">{rec.note}</p>
        </div>
        <div className="verdict-body">
          <p className="client">{analysis.client_name} · {analysis.project_name}</p>
          <p className="summary">{ev.summary}</p>
          <Gauge score={ev.overall_score} />
        </div>
      </section>

      <section className="block reveal" style={{ '--delay': '60ms' }}>
        <div className="block-head">
          <h2>Requirement coverage</h2>
          <p className="legend">
            {Object.keys(STATUS).filter((k) => statuses[k]).map((k) => (
              <span key={k}><i data-st={k} />{statuses[k]} {STATUS[k].label.toLowerCase()}</span>
            ))}
          </p>
        </div>
        <div className="coverage">
          {ev.requirements.map((r, i) => {
            const meta = reqMeta[r.id] || {}
            return (
              <button
                type="button" key={r.id} className="seg" data-st={r.status}
                style={{ '--i': i }} onClick={() => jump(r.id)}
                aria-label={`${meta.short_label || r.id}: ${STATUS[r.status]?.label}`}
                title={`${meta.short_label || r.id} — ${STATUS[r.status]?.label}`}
              >
                <span className="seg-glyph">{STATUS[r.status]?.glyph}</span>
                <span className="seg-label">{meta.short_label || r.id}</span>
                {meta.is_hard_constraint && <span className="seg-hard" title="Hard constraint">◆</span>}
              </button>
            )
          })}
        </div>
      </section>

      <section className="block reveal" style={{ '--delay': '120ms' }}>
        <div className="block-head">
          <h2>What was scored</h2>
          <p>{criteria.length} criteria, weighted by what this RFP asks for</p>
        </div>
        <div className="crit-grid">
          {criteria.map((c) => {
            const score = ev.scores[c.key]
            const tone = attentionTone(score, c.weight)
            return (
              <article className="crit" key={c.name}>
                <header>
                  <h3>{c.name}</h3>
                  <span className="score-chip" data-tone={tone}>{score}/5</span>
                </header>
                <div className="crit-meta">
                  <Pips score={score} />
                  <span className="weight" title="Weight in the overall score">×{c.weight}</span>
                  <span className="origin" data-origin={c.origin}>{ORIGIN[c.origin]}</span>
                </div>
                <p>{ev.rationales[c.key]}</p>
                <Citations items={ev.criterion_citations?.[c.key]} />
              </article>
            )
          })}
        </div>
      </section>

      <section className="block reveal" style={{ '--delay': '180ms' }}>
        <div className="block-head">
          <h2>Findings and fixes</h2>
          <p>{findings.length} items, most serious first</p>
        </div>
        <div className="findings">
          {findings.map((f) => {
            const req = f.requirement_ids?.[0]
            const meta = req ? reqMeta[req] : null
            const sev = SEVERITY[f.severity] || SEVERITY.minor
            return (
              <article className="finding" key={f.id} id={req ? 'req-' + req : f.id}
                       data-flash={flash && req === flash ? 'on' : undefined}>
                <div className="finding-head">
                  <span className="sev" data-tone={sev.tone}>{sev.label}</span>
                  <span className="kind">{KIND[f.kind] || f.kind}</span>
                  {meta && <span className="req-tag">{meta.short_label}{meta.is_hard_constraint ? ' ◆' : ''}</span>}
                </div>
                <p className="rationale">{f.rationale}</p>
                {f.rfp_quote && (
                  <p className="quote" data-src="rfp">
                    <Citation citation={{ source: 'rfp', found: true, label: meta ? `RFP, ${meta.source_section}` : 'RFP', quote: f.rfp_quote }} />
                    <span>{f.rfp_quote}</span>
                  </p>
                )}
                {f.response_quote ? (
                  <p className="quote" data-src="prop">
                    <Citation citation={{ source: 'proposal', found: true, label: 'In the proposal', quote: f.response_quote }} />
                    <span>{f.response_quote}</span>
                  </p>
                ) : (
                  <p className="quote" data-src="none">
                    <Citation citation={{ source: 'proposal', found: false, label: 'Not in the proposal', searched_terms: f.searched_terms || ['—'] }} />
                    <span>Nothing in the proposal matches this.</span>
                  </p>
                )}
                <FixBox text={f.suggested_fix} />
              </article>
            )
          })}
        </div>
      </section>

      <footer className="result-foot reveal" style={{ '--delay': '220ms' }}>
        <div>
          <strong>Review another proposal</strong>
          <p>The criteria are read from the RFP each time, so nothing carries over.</p>
        </div>
        <div className="foot-actions">
          {sampleId && (
            <div className="chips">
              {SAMPLES.map((s) => (
                <button type="button" key={s.id} className="chip" aria-pressed={sampleId === s.id}
                        onClick={() => sampleId !== s.id && onSample(s.id)}>
                  {s.chip}
                </button>
              ))}
            </div>
          )}
          <button type="button" className="btn btn-primary" onClick={onRestart}>Start over</button>
        </div>
      </footer>
    </div>
  )
}
