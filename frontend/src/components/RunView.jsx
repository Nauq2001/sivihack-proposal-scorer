import { useEffect, useState } from 'react'
import { reducedMotion } from '../lib/scoring.js'

/** Các bước của pipeline thật: RFP Analyst -> Scoring Agent -> kiểm chứng trích dẫn.
 *  Nhịp do giao diện đặt, không phải tiến độ thật của backend. */
export default function RunView({ steps, title, subtitle }) {
  const [done, setDone] = useState(0)

  useEffect(() => {
    const gap = reducedMotion() ? 80 : 700
    const timers = steps.map((_, i) => setTimeout(() => setDone(i + 1), (i + 1) * gap))
    return () => timers.forEach(clearTimeout)
  }, [steps])

  const pct = Math.min(100, (done / steps.length) * 100)

  return (
    <div className="run-view">
      <div className="run-card">
        <p className="eyebrow">Working</p>
        <h1>{title}</h1>
        <p className="lede">{subtitle}</p>

        <div className="run-track" role="progressbar" aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100}>
          <span className="run-fill" style={{ width: `${pct}%` }} />
        </div>

        <ol className="run-steps">
          {steps.map((step, i) => (
            <li key={step.title} data-state={i < done ? 'done' : i === done ? 'active' : 'idle'}>
              <span className="run-dot" />
              <span className="run-body">
                <strong>{step.title}</strong>
                <small>{i < done ? step.result : step.detail}</small>
              </span>
            </li>
          ))}
        </ol>
      </div>
    </div>
  )
}
