import { useRef, useState } from 'react'
import { SAMPLES } from '../data/samples.js'
import { CONVERTIBLE, PLAIN_TEXT } from '../api/review.js'
import { words } from '../lib/markdown.js'

const ACCEPT = [...PLAIN_TEXT, ...CONVERTIBLE].join(',')

function DocPane({ id, title, doc, busy, onChange, onUpload, children }) {
  const file = useRef(null)
  const [over, setOver] = useState(false)

  const take = (f) => { setOver(false); onUpload(f, null) }

  return (
    <section className={'pane' + (over ? ' over' : '')}
             onDragOver={(e) => { e.preventDefault(); setOver(true) }}
             onDragLeave={() => setOver(false)}
             onDrop={(e) => { e.preventDefault(); take(e.dataTransfer.files[0]) }}>
      <header className="pane-head">
        <div>
          <h2>{title}</h2>
          <span className="pane-file">{doc.name}</span>
        </div>
        <div className="pane-actions">
          {children}
          <button type="button" className="btn btn-ghost" disabled={busy} onClick={() => file.current.click()}>
            {busy ? 'Reading…' : 'Upload'}
          </button>
          <input type="file" ref={file} id={id + '-file'} accept={ACCEPT} hidden
                 onChange={(e) => onUpload(e.target.files[0], e.target)} />
        </div>
      </header>
      <textarea id={id} spellCheck="false" aria-label={title} value={doc.text} onChange={(e) => onChange(e.target.value)} />
      <footer className="pane-foot">
        {words(doc.text).toLocaleString('en')} words
        <span className="pane-hint">{busy ? 'Converting to text…' : 'Drop a PDF, Word, PowerPoint, image or text file'}</span>
      </footer>
    </section>
  )
}

export default function InputView({ rfp, proposal, sampleId, notice, converting, onRfp, onProposal, onSample, onUpload, onRun }) {
  const ready = rfp.text.trim().length > 40 && proposal.text.trim().length > 40 && !converting

  return (
    <div className="input-view">
      <div className="hero">
        <p className="eyebrow">Proposal review</p>
        <h1>An honest second opinion, before the client gets one</h1>
        <p className="lede">
          Drop in the client’s RFP and your draft. The reviewer pulls every requirement out of the RFP, scores the
          draft against them, and shows the exact sentence behind each finding.
        </p>
        <div className="hero-actions">
          <button type="button" className="btn btn-primary btn-lg" onClick={onRun} disabled={!ready}>
            Review this proposal
          </button>
          <span className="hero-hint">{ready ? 'Takes under a minute' : 'Paste both documents to start'}</span>
        </div>
      </div>

      <div className="samples">
        <span className="samples-label">Or load a sample proposal</span>
        <div className="chips">
          {SAMPLES.map((s) => (
            <button type="button" key={s.id} className="chip" aria-pressed={sampleId === s.id} onClick={() => onSample(s.id)}>
              {s.chip}<span className="chip-sub">{s.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="panes">
        <DocPane id="rfp-text" title="Client RFP" doc={rfp} busy={converting === 'rfp'}
                 onChange={onRfp} onUpload={(f, el) => onUpload('rfp', f, el)} />
        <DocPane id="prop-text" title="Draft proposal" doc={proposal} busy={converting === 'proposal'}
                 onChange={onProposal} onUpload={(f, el) => onUpload('proposal', f, el)} />
      </div>

      {notice && <p className="notice">{notice}</p>}
    </div>
  )
}
