import { useEffect, useRef, useState } from 'react'
import { Citations, Citation } from './Citation.jsx'
import { SAMPLES } from '../data/samples.js'
import {
  KIND, ORIGIN, RECOMMENDATION, SEVERITY, STATUS,
  attentionTone, countBy, reducedMotion, scoreTone, sortedFindings,
} from '../lib/scoring.js'

// Cung chu voi ba cot o man tieu chi. Khong hien "×3": nguoi dung khong chon
// mot con so, ho chon mot cot.
const PRIORITY = { high: 'High', medium: 'Medium', low: 'Low' }

// Ten luat cua backend/enterprise/evidence.py, viet lai cho nguoi ban doc.
const RULE_LABEL = {
  coverage_beyond_capability: 'Cover we do not staff',
  restoration_guarantee: 'A fix time we do not commit to',
  day_rate_below_floor: 'Below the rate card floor',
}

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

export default function ResultView({ result, source, error, sampleId, warnings = [], onSample, onRestart }) {
  const [flash, setFlash] = useState(null)
  const { rfp_analysis: analysis, confirmed_criteria: criteria, scoring } = result

  const statuses = countBy(scoring.findings, 'status')
  const reqMeta = Object.fromEntries(analysis.requirements.map((r) => [r.id, r]))
  const critMeta = Object.fromEntries(criteria.map((c) => [c.name, c]))
  const findings = sortedFindings(scoring.findings)
  const rec = RECOMMENDATION[scoring.recommendation] || RECOMMENDATION.revise
  const company = scoring.company_checks?.findings || []

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

      {warnings.length > 0 && (
        <p className="notice reveal">
          <strong>Heads up.</strong> {warnings.join(' ')} Everything else below is quoted word for word from the
          documents.
        </p>
      )}

      <section className="verdict reveal">
        <div className="verdict-score">
          <span className="pill" data-tone={rec.tone}>{rec.label}</span>
          <div className="score-big"><CountUp value={scoring.overall_score} /><small>/5</small></div>
          {/* Ly do do backend tinh, di kem chinh luat ra khuyen nghi; khong
              lay cau co dinh theo nhan nua, vi mot ban 1.4/5 va mot ban pha
              rang buoc cung deu la "Do not send" nhung khong cung mot ly do. */}
          <p className="score-note">{scoring.recommendation_reason || rec.note}</p>
        </div>
        <div className="verdict-body">
          <p className="client">{analysis.client_name} · {analysis.project_name}</p>
          <p className="summary">{scoring.verdict}</p>
          <Gauge score={scoring.overall_score} />
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
          {findings.slice().sort((a, b) => a.requirement_id.localeCompare(b.requirement_id)).map((f, i) => {
            const meta = reqMeta[f.requirement_id] || {}
            return (
              <button
                type="button" key={f.requirement_id} className="seg" data-st={f.status}
                style={{ '--i': i }} onClick={() => jump(f.requirement_id)}
                aria-label={`${meta.short_label || f.requirement_id}: ${STATUS[f.status]?.label}`}
                title={`${meta.short_label || f.requirement_id} — ${STATUS[f.status]?.label}`}
              >
                <span className="seg-glyph">{STATUS[f.status]?.glyph}</span>
                <span className="seg-label">{meta.short_label || f.requirement_id}</span>
                {meta.is_hard_constraint && <span className="seg-hard" title="Hard constraint">◆</span>}
              </button>
            )
          })}
        </div>
      </section>

      {company.length > 0 && (
        <section className="block reveal" style={{ '--delay': '90ms' }}>
          <div className="block-head">
            <h2>Promises your company has not signed off</h2>
            <p>Checked against the internal rate card and SLA standard — not against the RFP</p>
          </div>
          <div className="commitments">
            {company.map((f, i) => (
              <article className="commitment" key={i} data-sev={f.severity}>
                <header>
                  <span className="sev" data-tone={SEVERITY[f.severity]?.tone}>{SEVERITY[f.severity]?.label}</span>
                  <span className="kind">{RULE_LABEL[f.rule] || f.rule.replace(/_/g, ' ')}</span>
                  {f.standard?.is_current === false && <span className="stale">Standard out of date</span>}
                </header>
                <blockquote className="quote" data-src="prop">
                  <Citation citation={{ source: 'proposal', found: true, label: 'In the proposal', quote: f.quote }} />
                  <span>{f.quote}</span>
                </blockquote>
                <p className="rationale">{f.message}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="block reveal" style={{ '--delay': '120ms' }}>
        <div className="block-head">
          <h2>What was scored</h2>
          <p>{scoring.criteria.length} criteria, weighted by what this RFP asks for</p>
        </div>
        <div className="crit-grid">
          {scoring.criteria.map((sc) => {
            const c = critMeta[sc.name] || { weight: 1, origin: 'base' }
            const score = sc.score
            const tone = attentionTone(score, c.weight)
            return (
              <article className="crit" key={sc.name}>
                <header>
                  <h3>{sc.name}</h3>
                  <span className="score-chip" data-tone={tone}>{score}/5</span>
                </header>
                <div className="crit-meta">
                  <Pips score={score} />
                  <span className="weight" title="How much this counted in the overall score">
                    {PRIORITY[c.recommended_priority] || 'Medium'} priority
                  </span>
                  <span className="origin" data-origin={c.origin}>{ORIGIN[c.origin]}</span>
                </div>
                <p>{sc.comment}</p>
                {sc.citations?.length > 0 && (
                  <div className="cites">
                    {sc.citations.map((q, i) => (
                      <Citation key={i} citation={{ source: 'proposal', found: true, label: 'In the proposal', quote: q }} />
                    ))}
                  </div>
                )}
              </article>
            )
          })}
        </div>
      </section>

      <section className="block reveal" style={{ '--delay': '180ms' }}>
        <div className="block-head">
          <h2>Findings and fixes</h2>
          <p>{findings.length} requirements checked, most serious first</p>
        </div>
        <div className="findings">
          {findings.map((f) => {
            const meta = reqMeta[f.requirement_id] || {}
            const sev = SEVERITY[f.severity] || SEVERITY.medium
            const st = STATUS[f.status] || STATUS.vague
            return (
              <article className="finding" key={f.requirement_id} id={'req-' + f.requirement_id}
                       data-flash={flash === f.requirement_id ? 'on' : undefined}>
                <div className="finding-head">
                  <span className="sev" data-tone={sev.tone}>{sev.label}</span>
                  <span className="kind">{st.label}</span>
                  {meta.short_label && <span className="req-tag">{meta.short_label}{meta.is_hard_constraint ? ' ◆' : ''}</span>}
                </div>
                {meta.source_quote && (
                  <p className="quote" data-src="rfp">
                    <Citation citation={{ source: 'rfp', found: true, label: `RFP, ${meta.source_section}`, quote: meta.source_quote }} />
                    <span>{meta.text}</span>
                  </p>
                )}
                <p className="rationale">{f.reason}</p>
                {f.citation ? (
                  <p className="quote" data-src="prop">
                    <Citation citation={{ source: 'proposal', found: true, label: 'In the proposal', quote: f.citation }} />
                    <span>{f.citation}</span>
                  </p>
                ) : f.status !== 'met' && (
                  <p className="quote" data-src="none">
                    <Citation citation={{ source: 'proposal', found: false, label: 'Not in the proposal', searched_terms: [meta.short_label || f.requirement_id] }} />
                    <span>Nothing in the proposal matches this.</span>
                  </p>
                )}
                <FixBox text={f.suggested_patch} />
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
