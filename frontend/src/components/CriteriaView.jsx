import { useState } from 'react'

const LEVELS = [
  { id: 'high', label: 'High', note: 'Tied to a hard constraint in the RFP. A gap here can lose the deal.' },
  { id: 'medium', label: 'Medium', note: 'Tied to a stated requirement. Weighs on the decision.' },
  { id: 'low', label: 'Low', note: 'No direct requirement behind it. Moves the score a little.' },
]

const ORIGIN = {
  base: 'Base rubric',
  rfp_explicit: 'Stated in the RFP',
  ai_inferred: 'Read from the RFP',
  user: 'Added by the team',
}

function Card({ criterion }) {
  const [open, setOpen] = useState(false)
  return (
    <article className="crit-card" data-open={open}>
      <button type="button" className="crit-toggle" aria-expanded={open} onClick={() => setOpen((v) => !v)}>
        <span className="crit-name">{criterion.name}</span>
        {criterion.origin !== 'base' && <span className="tag" data-origin={criterion.origin}>RFP</span>}
        <svg className="chev" width="11" height="7" viewBox="0 0 11 7" aria-hidden="true">
          <path d="M1 1l4.5 4.5L10 1" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {open && (
        <div className="crit-card-body">
          <p className="crit-desc">{criterion.description}</p>
          <p className="crit-why">{criterion.priority_reason}</p>
          {criterion.source_refs?.length > 0 && (
            <ul className="crit-refs">
              {criterion.source_refs.map((r, i) => (
                <li key={i}><span className="ref-sec">{r.source_section}</span>{r.quote}</li>
              ))}
            </ul>
          )}
          <p className="crit-foot">{ORIGIN[criterion.origin] || criterion.origin} · weight ×{criterion.weight}</p>
        </div>
      )}
    </article>
  )
}

/** Tiêu chí do RFP Analyst chốt. Người dùng xem rồi chạy tiếp, không sửa —
 *  mức ưu tiên đến từ `recommended_priority` trong AI/contracts.py. */
export default function CriteriaView({ analysis, criteria, onRun }) {
  const ai = criteria.filter((c) => c.origin !== 'base').length

  return (
    <div className="criteria-view">
      <div className="hero">
        <p className="eyebrow">Step 2 of 3 · Read from the RFP</p>
        <h1>What this proposal will be judged on</h1>
        <p className="lede">
          {criteria.length} criteria, {ai > 0 ? `${ai} of them taken from this RFP rather than the base rubric` : 'all from the base rubric'}.
          Priority comes from whether a criterion is tied to a hard constraint. Open a card to see the reason and the
          quote behind it.
        </p>
        <div className="hero-actions">
          <button type="button" className="btn btn-primary btn-lg" onClick={onRun}>Score the proposal</button>
          <span className="hero-hint">{analysis.requirements.length} requirements · {analysis.requirements.filter((r) => r.is_hard_constraint).length} hard constraints</span>
        </div>
      </div>

      {analysis.detected_priority_note && (
        <aside className="priority-note reveal">
          <strong>What this client seems to care about</strong>
          <p>{analysis.detected_priority_note}</p>
        </aside>
      )}

      <div className="levels">
        {LEVELS.map((level, i) => {
          const cards = criteria.filter((c) => (c.recommended_priority || 'medium') === level.id)
          return (
            <section className="level reveal" key={level.id} style={{ '--delay': `${i * 70}ms` }} data-level={level.id}>
              <header>
                <h2>{level.label}</h2>
                <span className="level-count">{cards.length}</span>
                <p>{level.note}</p>
              </header>
              <div className="level-body">
                {cards.length === 0
                  ? <p className="level-empty">Nothing at this level.</p>
                  : cards.map((c) => <Card key={c.name} criterion={c} />)}
              </div>
            </section>
          )
        })}
      </div>
    </div>
  )
}
