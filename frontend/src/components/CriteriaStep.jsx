import { useState } from 'react'
import { PRIORITIES, PRIORITY_IDS, matchesSuggestion } from '../lib/scoring.js'
import { Citations } from './Citation.jsx'

/** One criterion. Moves between columns by drag, or by the arrow buttons —
 *  the arrows are what works on a phone and with a keyboard. */
function Card({ criterion, index, total, onMove, onRemove, onDragStart }) {
  const { id, name, description, source, why, citations, priority } = criterion
  const at = PRIORITY_IDS.indexOf(priority)

  return (
    <article className="card" draggable onDragStart={(e) => onDragStart(e, id)} data-source={source}>
      <h3>{name}</h3>
      <p className="card-desc">{description}</p>
      {source === 'ai' && <span className="tag">Read from the RFP</span>}
      {source === 'custom' && <span className="tag" data-kind="custom">Added by you</span>}
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
      <span className="sr-only">Card {index + 1} of {total}</span>
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
      <input autoFocus value={name} onChange={(e) => setName(e.target.value)} placeholder="Criterion, e.g. GDPR & data residency" aria-label="Criterion name" />
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
            Every criterion is reviewed. The column decides how much it pulls on the score: a Deal-breaker counts three
            times as much as a Minor one, and “Don’t score” keeps the finding but leaves it out of the number. Drag a
            card, or use its arrows.
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
            ? `Six base criteria, plus ${aiCount} the reviewer took from this RFP. Each card says why it sits where it does — check the quote before you trust the placement.`
            : 'Six base criteria. Run a review to get suggestions read from the RFP.'}
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
                  <span className="col-dot" />
                  <h2>{col.label}</h2>
                  <span className="col-weight">×{col.weight}</span>
                </div>
                <p>{col.hint}</p>
              </header>

              <div className="col-body">
                {cards.map((c, i) => (
                  <Card
                    key={c.id}
                    criterion={c}
                    index={i}
                    total={cards.length}
                    onMove={onMove}
                    onRemove={onRemove}
                    onDragStart={onDragStart}
                  />
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
        Overall score = each criterion’s score out of 5, averaged with these multipliers. Nothing is re-scored when you
        move a card; only the weighting changes.
      </p>
    </section>
  )
}
