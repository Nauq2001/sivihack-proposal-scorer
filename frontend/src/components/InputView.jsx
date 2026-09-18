import { useRef } from 'react'
import { SAMPLES } from '../data/samples.js'
import { words } from '../lib/markdown.js'

function DocPane({ id, title, doc, onChange, onUpload, children }) {
  const file = useRef(null)
  return (
    <section className="pane">
      <header className="pane-head">
        <div>
          <h2>{title}</h2>
          <span className="pane-file">{doc.name}</span>
        </div>
        <div className="pane-actions">
          {children}
          <button type="button" className="btn btn-ghost" onClick={() => file.current.click()}>Upload</button>
          <input type="file" ref={file} id={id + '-file'} accept=".md,.txt,.pdf" hidden
                 onChange={(e) => onUpload(e.target.files[0], e.target)} />
        </div>
      </header>
      <textarea id={id} spellCheck="false" aria-label={title} value={doc.text} onChange={(e) => onChange(e.target.value)} />
      <footer className="pane-foot">{words(doc.text).toLocaleString('en')} words</footer>
    </section>
  )
}

export default function InputView({ rfp, proposal, sampleId, notice, onRfp, onProposal, onSample, onUpload, onRun }) {
  const ready = rfp.text.trim().length > 40 && proposal.text.trim().length > 40

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
        <DocPane id="rfp-text" title="Client RFP" doc={rfp} onChange={onRfp} onUpload={(f, el) => onUpload('rfp', f, el)} />
        <DocPane id="prop-text" title="Draft proposal" doc={proposal} onChange={onProposal} onUpload={(f, el) => onUpload('proposal', f, el)} />
      </div>

      {notice && <p className="notice">{notice}</p>}
    </div>
  )
}
