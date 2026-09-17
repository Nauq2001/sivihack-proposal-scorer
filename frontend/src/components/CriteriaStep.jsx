import { Fragment } from 'react'
import { CRITERIA, LEVELS, DEFAULT_LEVELS } from '../lib/scoring.js'
import { Citations } from './Citation.jsx'

export default function CriteriaStep({ levels, suggested, priorities, onLevel, onLevels, onGo, onRun }) {
  const isSuggested = suggested && CRITERIA.every((c) => levels[c.id] === suggested[c.id])

  return (
    <section>
      <div className="view-head">
        <div>
          <h1>Decide what matters for this client</h1>
          <p className="lede">
            Set how much each criterion counts: Low, Medium or High. A High criterion counts three times as much as a
            Low one. The overall score updates straight away; no re-run needed.
          </p>
        </div>
        <div className="actions">
          <button type="button" className="btn" onClick={() => onGo('docs')}>Back to documents</button>
          <button type="button" className="btn btn-primary" onClick={onRun}>Run review</button>
        </div>
      </div>

      <div className="crit-layout">
        <div className="panel">
          {CRITERIA.map((c) => (
            <div className="crit-row" key={c.id}>
              <div className="crit-name">
                <strong>{c.name}</strong>
                <span>{c.description}</span>
              </div>
              <fieldset className="seg">
                <legend>Weight for {c.name}</legend>
                {LEVELS.map(([value, label]) => (
                  <Fragment key={value}>
                    <input
                      type="radio"
                      name={'lvl-' + c.id}
                      id={`lvl-${c.id}-${value}`}
                      value={value}
                      checked={levels[c.id] === value}
                      onChange={() => onLevel(c.id, value)}
                    />
                    <label htmlFor={`lvl-${c.id}-${value}`} data-lvl={value}>{label}</label>
                  </Fragment>
                ))}
              </fieldset>
            </div>
          ))}
        </div>

        <aside className="panel priorities">
          <h2>What this client cares about</h2>
          <p>Read from the RFP. Check the quotes, then apply the suggested weights or set your own.</p>
          {priorities.map((p) => (
            <div className="prio" key={p.id}>
              <h3>{p.title}</h3>
              <p>{p.text}</p>
              <Citations items={p.citations} />
              <div className="boost">Suggested: {p.suggestion}</div>
            </div>
          ))}
          <div className="prio">
            <p>
              Problem understanding and Scope are suggested at Low: Completeness already checks them against each RFP
              requirement, so a higher weight would count the same gaps twice.
            </p>
          </div>
          <button
            type="button"
            className={'btn' + (isSuggested ? '' : ' btn-primary')}
            onClick={() => onLevels(isSuggested ? DEFAULT_LEVELS : suggested)}
            disabled={!suggested}
          >
            {isSuggested ? 'Set all to Medium' : 'Apply suggested weights'}
          </button>
        </aside>
      </div>
    </section>
  )
}
