import { useContext, useMemo, useState } from 'react'
import { CitationContext } from './Citation.jsx'

/** Ba cot. `weight` gui sang /api/score lay tu cot, vi hop dong ghi ro
 *  confirmed_criteria la nguon su that sau buoc nguoi dung duyet.
 *  Khong can tieu chi nao thi xoa han, khong co cot "de sang mot ben". */
export const COLUMNS = [
  { id: 'high', label: 'High', weight: 3, note: 'Tied to a hard constraint. A gap here can lose the deal.' },
  { id: 'medium', label: 'Medium', weight: 2, note: 'Tied to a stated requirement. Weighs on the decision.' },
  { id: 'low', label: 'Low', weight: 1, note: 'No direct requirement behind it. Moves the score a little.' },
]

const COLUMN_IDS = COLUMNS.map((c) => c.id)

const ORIGIN = {
  base: null,                       // mac dinh, khong can nhan
  rfp_explicit: 'From the RFP',
  ai_inferred: 'Read from the RFP',
  user: 'Added by you',
}

/** Ly do de xuat muc do, viet lai tu du lieu.
 *
 *  Ban tu agent ghi "Contains hard RFP requirement REQ-004." — REQ-004 la so
 *  thu tu noi bo, nguoi doc RFP khong tra ra duoc no nam o dau. */
function reasonFor(criterion, linked) {
  if (criterion.origin === 'user' || !linked.length) return criterion.priority_reason
  const hard = linked.find((r) => r.is_hard_constraint)
  if (hard) return `${labelOf(hard)} is a hard constraint — the client will not trade it away.`
  return `Tied to ${linked.length} requirement${linked.length > 1 ? 's' : ''} the RFP states outright.`
}

const labelOf = (r) => r.short_label || r.source_section || r.id

/** Tung yeu cau mot dong, bam vao mo dung doan trong RFP.
 *
 *  Ba dong dau la du de biet tieu chi nay soi cai gi; con lai mo ra khi can,
 *  vi "Completeness" om ca danh sach yeu cau. */
function Requirements({ linked }) {
  const openCitation = useContext(CitationContext)
  const [all, setAll] = useState(false)
  if (!linked.length) return null

  const shown = all ? linked : linked.slice(0, 3)
  const hard = linked.filter((r) => r.is_hard_constraint).length

  return (
    <div className="crit-reqs">
      <p className="reqs-head">
        Checks {linked.length} requirement{linked.length > 1 ? 's' : ''} from the RFP
        {hard > 0 && <span className="reqs-hard">{hard} hard</span>}
      </p>
      <ul>
        {shown.map((r) => (
          <li key={r.id}>
            <button
              type="button" className="req" data-hard={r.is_hard_constraint || undefined}
              title={`${labelOf(r)} — open this in the RFP`}
              onClick={() => openCitation({ source: 'rfp', found: true, label: labelOf(r), quote: r.source_quote })}
            >
              <em>{labelOf(r)}</em>
              <span>{r.text}</span>
            </button>
          </li>
        ))}
      </ul>
      {linked.length > 3 && (
        <button type="button" className="btn-quiet reqs-more" onClick={() => setAll(!all)}>
          {all ? 'Show fewer' : `Show all ${linked.length}`}
        </button>
      )}
    </div>
  )
}

function Card({ criterion, requirementById, suggestedPriority, onMove, onRemove, onDragStart }) {
  const priority = criterion.recommended_priority || 'medium'
  const at = COLUMN_IDS.indexOf(priority)
  const badge = ORIGIN[criterion.origin]
  const linked = (criterion.requirement_ids || []).map((id) => requirementById[id]).filter(Boolean)
  const why = reasonFor(criterion, linked)
  // Ly do ben duoi van la su that ve yeu cau, khong doi theo cot. Nhung neu
  // khong noi ro nguoi dung da doi cot, the bai doc nhu dang tu mau thuan.
  const moved = suggestedPriority && suggestedPriority !== priority

  return (
    <article className="crit-card" draggable onDragStart={(e) => onDragStart(e, criterion.name)}>
      <header className="crit-head">
        <span className="grip" aria-hidden="true">⠿</span>
        <h3>{criterion.name}</h3>
        {moved
          ? <span className="tag moved">Moved from {COLUMNS.find((c) => c.id === suggestedPriority)?.label}</span>
          : badge && <span className="tag" data-origin={criterion.origin}>{badge}</span>}
      </header>

      {criterion.description && <p className="crit-desc">{criterion.description}</p>}
      {why && <p className="crit-why">{why}</p>}

      <Requirements linked={linked} />

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
        <button type="button" className="icon-btn remove" onClick={() => onRemove(criterion.name)} aria-label={`Remove ${criterion.name}`}>
          <svg width="11" height="11" viewBox="0 0 14 14" aria-hidden="true">
            <path d="M2 2l10 10M12 2L2 12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          </svg>
        </button>
      </div>
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

export default function CriteriaView({ analysis, criteria, suggested = [], onChange, onReset, onRun, warnings = [] }) {
  const [adding, setAdding] = useState(null)
  const [over, setOver] = useState(null)
  const [merged, setMerged] = useState(null)
  const requirementById = useMemo(
    () => Object.fromEntries((analysis.requirements || []).map((r) => [r.id, r])),
    [analysis.requirements],
  )
  const suggestedPriority = useMemo(
    () => Object.fromEntries(suggested.map((c) => [c.name, c.recommended_priority])),
    [suggested],
  )

  /** Yeu cau khong con tieu chi nao soi toi.
   *
   *  Xoa mot tieu chi khong xoa yeu cau: agent van cham tung yeu cau va van
   *  bao thieu, nhung khong con o nao gom chung lai thanh diem. Im lang o day
   *  la cach de mot ban thieu nua so yeu cau van ra diem dep. */
  const uncovered = useMemo(() => {
    const covered = new Set(criteria.flatMap((c) => c.requirement_ids || []))
    return (analysis.requirements || []).filter((r) => !covered.has(r.id))
  }, [criteria, analysis.requirements])

  const priorityOf = (c) => (COLUMN_IDS.includes(c.recommended_priority) ? c.recommended_priority : 'medium')
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

  /** Gom trung ten thay vi them ban thu hai — giong `add_or_merge` cua agent
   *  (agent/src/rfp_analyst/criteria.py): ban trung giu criterion chuan, chi
   *  nhan muc do moi. So khop bo dau cach thua va phan biet hoa thuong, y het
   *  `_normalize` ben do, de "pricing  clarity" cung bat duoc. */
  const add = (priority, name, description) => {
    const key = (s) => String(s).toLowerCase().split(/\s+/).filter(Boolean).join(' ')
    const existing = criteria.find((c) => key(c.name) === key(name))
    if (existing) {
      setPriority(existing.name, priority)
      setAdding(null)
      setMerged(existing.name)
      return
    }
    onChange([...criteria, {
      name, description, weight: COLUMNS.find((c) => c.id === priority)?.weight || 1,
      recommended_priority: priority, priority_reason: 'Added by you for this review.',
      origin: 'user', source_refs: [], requirement_ids: [],
    }])
    setAdding(null)
    setMerged(null)
  }

  const fromRfp = criteria.filter((c) => c.origin === 'ai_inferred' || c.origin === 'rfp_explicit').length

  return (
    <div className="criteria-view">
      <div className="hero">
        <p className="eyebrow">Step 2 of 3 · Read from the RFP, yours to adjust</p>
        <h1>What this proposal will be judged on</h1>
        <p className="lede">
          {criteria.length} criteria{fromRfp > 0 ? `, ${fromRfp} of them proposed from this RFP` : ', all from the base rubric — this RFP did not call for extra ones'}.
          Drag a card to another column or use its arrows. Remove anything you don’t want scored, and add your own.
        </p>
        <div className="hero-actions">
          <button type="button" className="btn btn-primary btn-lg" onClick={onRun} disabled={criteria.length === 0}>
            Score the proposal
          </button>
          <span className="hero-hint">
            {criteria.length} criteria · {analysis.requirements.length} requirements ·{' '}
            {analysis.requirements.filter((r) => r.is_hard_constraint).length} hard constraints
          </span>
          <button type="button" className="btn btn-ghost" onClick={onReset}>Reset to the RFP suggestion</button>
        </div>
      </div>

      {merged && (
        <p className="notice reveal">
          <strong>Already on the board.</strong> “{merged}” was moved to the column you picked instead of being
          added twice.
        </p>
      )}

      {warnings.length > 0 && (
        <p className="notice reveal">
          <strong>Heads up.</strong> {warnings.join(' ')}
        </p>
      )}

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
                  <Card key={c.name} criterion={c} requirementById={requirementById}
                        suggestedPriority={suggestedPriority[c.name]} onMove={move}
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

      {uncovered.length > 0 && (
        <p className="notice board-notice">
          <strong>{uncovered.length} requirement{uncovered.length > 1 ? 's' : ''} no longer count toward the score.</strong>{' '}
          {/* Hai yeu cau tach tu mot dong RFP mang cung nhan, chi ke mot lan. */}
          {[...new Set(uncovered.map((r) => r.short_label || r.id))].join(', ')} —{' '}
          {uncovered.length > 1 ? 'they are' : 'it is'} still checked and reported, but no remaining criterion
          scores {uncovered.length > 1 ? 'them' : 'it'}. Keep “Completeness vs RFP Requirements” to cover everything.
        </p>
      )}

      <p className="board-foot">
        The column decides how much a criterion counts when the proposal is scored. Nothing is scored yet.
      </p>
    </div>
  )
}
