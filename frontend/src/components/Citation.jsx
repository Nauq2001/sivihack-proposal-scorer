import { createContext, useContext } from 'react'

/** Lets any nested card open a citation in the source pane. */
export const CitationContext = createContext(() => {})

export function Citation({ citation }) {
  const open = useContext(CitationContext)
  const missing = citation.found === false
  return (
    <button
      type="button"
      className={'cite' + (missing ? ' missing' : '')}
      data-doc={citation.source === 'rfp' ? 'rfp' : 'prop'}
      onClick={() => open(citation)}
    >
      {citation.label}
    </button>
  )
}

export function Citations({ items }) {
  if (!items || !items.length) return null
  return (
    <div className="cites">
      {items.map((c, i) => (
        <Citation key={i} citation={c} />
      ))}
    </div>
  )
}
