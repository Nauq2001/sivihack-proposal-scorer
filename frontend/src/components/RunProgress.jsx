import { useEffect, useState } from 'react'

/** Shows what the reviewer is doing while the request is in flight. The steps
 *  are paced by the UI, not reported by the backend. */
export default function RunProgress({ steps, rfpName, proposalName }) {
  const [done, setDone] = useState(0)
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  useEffect(() => {
    const timers = steps.map((_, i) => setTimeout(() => setDone(i + 1), (i + 1) * (reduce ? 60 : 520)))
    return () => timers.forEach(clearTimeout)
  }, [steps, reduce])

  return (
    <div className="panel run" aria-live="polite">
      <h2>Reviewing {proposalName}</h2>
      <p>Against {rfpName}</p>
      <ol>
        {steps.map((s, i) => (
          <li key={s[0]} data-s={i < done ? 'done' : i === done ? 'active' : 'pending'}>
            <span className="dot" />
            <span>
              {s[0]}
              <small>{s[1]}</small>
            </span>
          </li>
        ))}
      </ol>
    </div>
  )
}
