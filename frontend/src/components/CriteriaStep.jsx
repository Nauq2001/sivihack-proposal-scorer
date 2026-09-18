import { useState } from 'react'
import { PRIORITIES, PRIORITY_IDS, matchesSuggestion } from '../lib/scoring.js'
import { Citations } from './Citation.jsx'

/** A criterion card: the name only, until you open it. Moves between columns by
 *  drag, or by the arrow buttons — the arrows are what works on a phone and
 *  with a keyboard. */
function Card({ criterion, onMove, onRemove, onDragStart }) {
  const [open, setOpen] = useState(false)
  const { id, name, description, source, why, citations, priority } = criterion
  const at = PRIORITY_IDS.indexOf(priority)

  return (
    <article className="card" draggable onDragStart={(e) => onDragStart(e, id)} data-source={source} data-open={open}>
      <button type="button" className="card-toggle" aria-expanded={open} onClick={() => setOpen((v) => !v)}>
        <span className="card-name">{name}</span>
        {source === 'ai' && <span className="tag" title="Read from this RFP">RFP</span>}
        {source === 'custom' && <span className="tag" data-kind="custom" title="Added by you">You</span>}
        <svg className="chev" width="11" height="7" viewBox="0 0 11 7" aria-hidden="true">
          <path d="M1 1l4.5 4.5L10 1" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {open && (
        <div className="card-body">
          <p className="card-desc">{description}</p>
          {why && <p className="card-why">{why}</p>}
          <Citations items={citations} />
          <div className="card-actions">
            <button type="button" className="icon-btn" onClick={() => onMove(id, -1)} disabled={at === 0} aria-label={`Move ${name} one column more important`}>←</button>
            <button type="button" className="icon-btn" onClick={() => onMove(id, 1)} disabled={at === PRIORITY_IDS.length - 1} aria-label={`Move ${name} one column less important`}>→</button>
            <button type="button" className="icon-btn remove" onClick={() => onRemove(id)} aria-label={`Remove ${name}`}>
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
    <form
      className="add-card"
      onSubmit={(e) => {
        e.preventDefault()
        if (!name.trim()) return
        onAdd(name.trim(), description.trim())
        setName('')
        setDescription('')
      }}
    >
      <input autoFocus value={name} onChange={(e) => setName(e.target.value)} placeholder="Criterion" aria-label="Criterion name" />
      <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What to check" aria-label="What to check" />
      <div className="add-card-actions">
        <button type="submit" className="btn btn-primary">Add</button>
        <button type="button" className="btn" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  )
}

export default function CriteriaStep({ criteria, onPriority, onMove, onRemove, onAdd, onReset, onGo, onRun }) {
  const [adding, setAdding] = useState(null)
  const [over, setOver] = useState(null)

  const onDragStart = (e, id) => {
    e.dataTransfer.setData('text/plain', id)
    e.dataTransfer.effectAllowed = 'move'
  }
  const onDrop = (e, priority) => {
    e.preventDefault()
    const id = e.dataTransfer.getData('text/plain')
    setOver(null)
    if (id) onPriority(id, priority)
  }

  const suggested = matchesSuggestion(criteria)
  const aiCount = criteria.filter((c) => c.source === 'ai').length

  return (
    <section>
      <div className="view-head">
        <div>
          <h1>Decide what matters for this client</h1>
          <p className="lede">
            Every criterion is reviewed. The column decides how much it pulls the overall score. Open a card to see
            what it checks and why the reviewer put it there.
          </p>
        </div>
        <div className="actions">
          <button type="button" className="btn" onClick={() => onGo('docs')}>Back to documents</button>
          <button type="button" className="btn btn-primary" onClick={onRun}>Run review</button>
        </div>
      </div>

      <div className="board-bar">
        <p>
          {aiCount > 0
            ? `Seven standard criteria, plus ${aiCount} the reviewer read out of this RFP. Drag a card to another column, or open it and use the arrows.`
            : 'Seven standard criteria. Run a review to get suggestions read from the RFP.'}
        </p>
        <button type="button" className={'btn' + (suggested ? '' : ' btn-primary')} onClick={onReset} disabled={suggested}>
          {suggested ? 'Following the RFP suggestion' : 'Reset to RFP suggestion'}
        </button>
      </div>

      <div className="board">
        {PRIORITIES.map((col) => {
          const cards = criteria.filter((c) => c.priority === col.id)
          return (
            <section
              key={col.id}
              className={'column' + (over === col.id ? ' over' : '')}
              data-prio={col.id}
              onDragOver={(e) => { e.preventDefault(); setOver(col.id) }}
              onDragLeave={() => setOver((o) => (o === col.id ? null : o))}
              onDrop={(e) => onDrop(e, col.id)}
            >
              <header className="col-head">
                <div className="col-title">
                  <h2>{col.label}</h2>
                  <span className="col-count">{cards.length}</span>
                </div>
                <p className="col-note">{col.hint}</p>
              </header>

              <div className="col-body">
                {cards.map((c) => (
                  <Card key={c.id} criterion={c} onMove={onMove} onRemove={onRemove} onDragStart={onDragStart} />
                ))}

                {adding === col.id ? (
                  <AddForm onAdd={(name, description) => { onAdd({ name, description, priority: col.id }); setAdding(null) }} onCancel={() => setAdding(null)} />
                ) : (
                  <button type="button" className="add-btn" onClick={() => setAdding(col.id)}>+ Add criterion</button>
                )}
              </div>
            </section>
          )
        })}
      </div>

      <p className="board-foot">
        Moving a card changes only how much that criterion counts. Nothing is scored again, so the overall score
        updates as soon as you drop it.
      </p>
    </section>
  )
}
