import { useRef, useState } from 'react'
import { SAMPLES } from '../data/samples.js'
import { Citations } from './Citation.jsx'
import {
  PRIORITIES, PRIORITY_LABEL, PRIORITY_WEIGHT, STATUS_GLYPH, STATUS_LABEL,
  attentionTone, overallScore, scoreTone, verdictOf, weightNote,
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

/** Where the score sits against the two thresholds that change the verdict. */
function Gauge({ score }) {
  return (
    <div className="gauge">
      <div className="gauge-track" role="img" aria-label={`${score.toFixed(1)} out of 5`}>
        <span className="zone" data-tone="bad" />
        <span className="zone" data-tone="warn" />
        <span className="zone" data-tone="good" />
        <span className="gauge-mark" style={{ left: `${Math.min(100, Math.max(0, (score / 5) * 100))}%` }} />
      </div>
      <div className="gauge-labels">
        <span>Not ready</span>
        <span>Revise</span>
        <span>Ready</span>
      </div>
    </div>
  )
}

function Pips({ score, tone }) {
  return (
    <span className="pips" data-tone={tone || scoreTone(score)} aria-label={`${score} out of 5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <i key={n} className={'pip' + (n <= score ? ' on' : '')} />
      ))}
    </span>
  )
}

export default function ReviewStep({ result, criteria, sampleId, source, error, onSample, onRun, onGo }) {
  const [flash, setFlash] = useState(null)
  const [filter, setFilter] = useState('all')

  const byId = Object.fromEntries(result.criteria.map((c) => [c.id, c]))
  const { score } = overallScore(criteria, byId)
  const [tone, verdict] = verdictOf(score)
  const ordered = PRIORITIES.flatMap((p) => criteria.filter((c) => c.priority === p.id))

  const counts = { met: 0, partial: 0, missing: 0, conflict: 0 }
  result.requirements.forEach((r) => { counts[r.status] += 1 })
  const problems = result.requirements.filter((r) => r.status !== 'met')
  const shown = filter === 'problems' ? problems : result.requirements

  const jump = (id) => {
    setFilter('all')
    requestAnimationFrame(() => {
      const el = document.getElementById('req-' + id)
      if (!el) return
      el.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' })
      setFlash(null)
      requestAnimationFrame(() => setFlash(id))
    })
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
        <div className="verdict-score">
          <div className="score-big">{score.toFixed(1)}<small>/5</small></div>
          <span className="pill" data-tone={tone}>{verdict}</span>
          <div className="score-cap">{weightNote(criteria)}</div>
        </div>
        <div className="verdict-body">
          <p className="summary">{result.overall.summary}</p>
          <Gauge score={score} />
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
          <h2>Scores by criterion</h2>
          <p>Heaviest criteria first. Red is what is dragging the score down most.</p>
        </div>
        <div className="cr-grid">
          {ordered.map((c) => {
            const s = byId[c.id]
            const counted = PRIORITY_WEIGHT[c.priority] > 0
            return (
              <article className="cr-card" key={c.id} data-off={!counted || !s}>
                <div className="cr-card-head">
                  <h3>{c.name}</h3>
                  <span className="score-chip" data-tone={s ? attentionTone(s.score, c.priority) : undefined}>{s ? `${s.score}/5` : '–'}</span>
                </div>
                <div className="cr-card-meta">
                  {s && <Pips score={s.score} tone={attentionTone(s.score, c.priority)} />}
                  <span className="lvl">{PRIORITY_LABEL[c.priority]}{counted ? '' : ' — not counted'}</span>
                </div>
                <p>{s ? s.comment : 'Added after this run. Run the review again to score it.'}</p>
                {s && <Citations items={s.citations} />}
              </article>
            )
          })}
        </div>
      </section>

      <section className="block">
        <div className="block-head">
          <h2>Requirements and fixes</h2>
          <div className="filter" role="group" aria-label="Filter requirements">
            <button type="button" className="chip" aria-pressed={filter === 'all'} onClick={() => setFilter('all')}>
              All {result.requirements.length}
            </button>
            <button type="button" className="chip" aria-pressed={filter === 'problems'} onClick={() => setFilter('problems')}>
              Needs work {problems.length}
            </button>
          </div>
        </div>
        <div className="panel">
          {shown.length === 0 && (
            <p className="empty">Every requirement in the RFP is addressed. Nothing to fix here.</p>
          )}
          {shown.map((r) => (
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
