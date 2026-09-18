import { useState } from 'react'

/** Bon cot. `weight` gui sang /api/score lay tu cot, vi hop dong ghi ro
 *  confirmed_criteria la nguon su that sau buoc nguoi dung duyet.
 *  Cot "Don't score" = bo tieu chi do ra khoi danh sach gui di (contract bat
 *  buoc weight > 0, nen khong the gui weight 0). */
export const COLUMNS = [
  { id: 'high', label: 'High', weight: 3, note: 'Tied to a hard constraint. A gap here can lose the deal.' },
  { id: 'medium', label: 'Medium', weight: 2, note: 'Tied to a stated requirement. Weighs on the decision.' },
  { id: 'low', label: 'Low', weight: 1, note: 'No direct requirement behind it. Moves the score a little.' },
  { id: 'skip', label: 'Don’t score', weight: 0, note: 'Left out of this run entirely.' },
]

const COLUMN_IDS = COLUMNS.map((c) => c.id)

const ORIGIN = {
  base: 'Base rubric',
  rfp_explicit: 'Stated in the RFP',
  ai_inferred: 'Read from the RFP',
  user: 'Added by you',
}

function Card({ criterion, onMove, onRemove, onDragStart }) {
  const [open, setOpen] = useState(false)
  const at = COLUMN_IDS.indexOf(criterion.recommended_priority || 'medium')

  return (
    <article className="crit-card" data-open={open} draggable onDragStart={(e) => onDragStart(e, criterion.name)}>
      <button type="button" className="crit-toggle" aria-expanded={open} onClick={() => setOpen((v) => !v)}>
        <span className="grip" aria-hidden="true">⠿</span>
        <span className="crit-name">{criterion.name}</span>
        {criterion.origin === 'user' && <span className="tag" data-origin="user">You</span>}
        {criterion.origin && criterion.origin !== 'base' && criterion.origin !== 'user' && <span className="tag">RFP</span>}
        <svg className="chev" width="11" height="7" viewBox="0 0 11 7" aria-hidden="true">
          <path d="M1 1l4.5 4.5L10 1" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {open && (
        <div className="crit-card-body">
          {criterion.description && <p className="crit-desc">{criterion.description}</p>}
          {criterion.priority_reason && <p className="crit-why">{criterion.priority_reason}</p>}
          {criterion.source_refs?.length > 0 && (
            <ul className="crit-refs">
              {criterion.source_refs.map((r, i) => (
                <li key={i}><span className="ref-sec">{r.source_section}</span>{r.quote}</li>
              ))}
            </ul>
          )}
          <div className="crit-actions">
            <button type="button" className="icon-btn" onClick={() => onMove(criterion.name, -1)} disabled={at === 0}
                    aria-label={`Move ${criterion.name} one column more important`}>←</button>
            <button type="button" className="icon-btn" onClick={() => onMove(criterion.name, 1)} disabled={at === COLUMN_IDS.length - 1}
                    aria-label={`Move ${criterion.name} one column less important`}>→</button>
            <span className="crit-origin">{ORIGIN[criterion.origin] || 'Base rubric'}</span>
            <button type="button" className="icon-btn remove" onClick={() => onRemove(criterion.name)} aria-label={`Remove ${criterion.name}`}>
              <svg width="11" height="11" viewBox="0 0 14 14" aria-hidden="true">
                <path d="M2 2l10 10M12 2L2 12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </article>
  )
}

function AddForm({ onAdd, onCancel }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  return (
    <form className="add-card" onSubmit={(e) => { e.preventDefault(); if (name.trim()) onAdd(name.trim(), description.trim()) }}>
      <input autoFocus value={name} onChange={(e) => setName(e.target.value)} placeholder="Criterion" aria-label="Criterion name" />
      <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What to check" aria-label="What to check" />
      <div className="add-card-actions">
        <button type="submit" className="btn btn-primary">Add</button>
        <button type="button" className="btn" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  )
}

export default function CriteriaView({ analysis, criteria, onChange, onReset, onRun }) {
  const [adding, setAdding] = useState(null)
  const [over, setOver] = useState(null)

  const priorityOf = (c) => c.recommended_priority || 'medium'
  const setPriority = (name, priority) =>
    onChange(criteria.map((c) => (c.name === name ? { ...c, recommended_priority: priority } : c)))

  const move = (name, dir) => {
    const current = criteria.find((c) => c.name === name)
    if (!current) return
    const next = COLUMN_IDS[Math.min(COLUMN_IDS.length - 1, Math.max(0, COLUMN_IDS.indexOf(priorityOf(current)) + dir))]
    setPriority(name, next)
  }

  const onDragStart = (e, name) => {
    e.dataTransfer.setData('text/plain', name)
    e.dataTransfer.effectAllowed = 'move'
  }
  const onDrop = (e, priority) => {
    e.preventDefault()
    setOver(null)
    const name = e.dataTransfer.getData('text/plain')
    if (name) setPriority(name, priority)
  }

  const add = (priority, name, description) => {
    if (criteria.some((c) => c.name.toLowerCase() === name.toLowerCase())) return
    onChange([...criteria, {
      name, description, weight: COLUMNS.find((c) => c.id === priority)?.weight || 1,
      recommended_priority: priority, priority_reason: 'Added by you for this review.',
      origin: 'user', source_refs: [],
    }])
    setAdding(null)
  }

  const scored = criteria.filter((c) => priorityOf(c) !== 'skip').length
  const ai = criteria.filter((c) => c.origin && c.origin !== 'base').length

  return (
    <div className="criteria-view">
      <div className="hero">
        <p className="eyebrow">Step 2 of 3 · Read from the RFP, yours to adjust</p>
        <h1>What this proposal will be judged on</h1>
        <p className="lede">
          {criteria.length} criteria{ai > 0 ? `, ${ai} of them taken from this RFP` : ''}. Drag a card to another
          column, or open it and use the arrows. Anything in “Don’t score” is left out of this run.
        </p>
        <div className="hero-actions">
          <button type="button" className="btn btn-primary btn-lg" onClick={onRun} disabled={scored === 0}>
            Score the proposal
          </button>
          <span className="hero-hint">
            {scored} of {criteria.length} criteria · {analysis.requirements.length} requirements ·{' '}
            {analysis.requirements.filter((r) => r.is_hard_constraint).length} hard constraints
          </span>
          <button type="button" className="btn btn-ghost" onClick={onReset}>Reset to the RFP suggestion</button>
        </div>
      </div>

      {analysis.detected_priority_note && (
        <aside className="priority-note reveal">
          <strong>What this client seems to care about</strong>
          <p>{analysis.detected_priority_note}</p>
        </aside>
      )}

      <div className="levels">
        {COLUMNS.map((col, i) => {
          const cards = criteria.filter((c) => priorityOf(c) === col.id)
          return (
            <section
              className={'level reveal' + (over === col.id ? ' over' : '')} key={col.id}
              style={{ '--delay': `${i * 60}ms` }} data-level={col.id}
              onDragOver={(e) => { e.preventDefault(); setOver(col.id) }}
              onDragLeave={() => setOver((o) => (o === col.id ? null : o))}
              onDrop={(e) => onDrop(e, col.id)}
            >
              <header>
                <h2>{col.label}</h2>
                <span className="level-count">{cards.length}</span>
                <p>{col.note}</p>
              </header>
              <div className="level-body">
                {cards.map((c) => (
                  <Card key={c.name} criterion={c} onMove={move}
                        onRemove={(name) => onChange(criteria.filter((x) => x.name !== name))}
                        onDragStart={onDragStart} />
                ))}
                {adding === col.id
                  ? <AddForm onAdd={(name, description) => add(col.id, name, description)} onCancel={() => setAdding(null)} />
                  : <button type="button" className="add-btn" onClick={() => setAdding(col.id)}>+ Add criterion</button>}
              </div>
            </section>
          )
        })}
      </div>

      <p className="board-foot">
        Moving a card changes how much that criterion counts when the proposal is scored. Nothing is scored yet.
      </p>
    </div>
  )
}
