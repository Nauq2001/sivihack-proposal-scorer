import { useRef } from 'react'
import { SAMPLES } from '../data/samples.js'
import { words } from '../lib/markdown.js'

function DocCard({ title, doc, onChange, onUpload, children, inputId }) {
  const file = useRef(null)
  return (
    <div className="doc-card">
      <div className="doc-head">
        <h2>{title}</h2>
        <span className="file">{doc.name}</span>
        <div className="actions">
          {children}
          <button type="button" className="btn" onClick={() => file.current.click()}>Upload</button>
          <input type="file" ref={file} id={inputId} accept=".md,.txt,.pdf" hidden onChange={(e) => onUpload(e.target.files[0], e.target)} />
        </div>
      </div>
      <textarea
        id={inputId + '-text'}
        spellCheck="false"
        aria-label={title + ' text'}
        value={doc.text}
        onChange={(e) => onChange(e.target.value)}
      />
      <div className="doc-foot">
        <span>{words(doc.text).toLocaleString('en')} words</span>
        <span>Markdown or plain text</span>
      </div>
    </div>
  )
}

export default function DocumentsStep({ rfp, proposal, sampleId, notice, onRfp, onProposal, onSample, onUpload, onGo, onRun }) {
  return (
    <section>
      <div className="view-head">
        <div>
          <h1>Add the RFP and the draft proposal</h1>
          <p className="lede">
            Paste the text or upload a Markdown file. The reviewer checks the proposal against every requirement in the
            RFP, so both documents are needed.
          </p>
        </div>
        <div className="actions">
          <button type="button" className="btn" onClick={() => onGo('criteria')}>Set criteria</button>
          <button type="button" className="btn btn-primary" onClick={onRun}>Run review</button>
        </div>
      </div>

      <div className="docs-grid">
        <DocCard title="Client RFP" inputId="rfp" doc={rfp} onChange={onRfp} onUpload={(f, el) => onUpload('rfp', f, el)} />
        <DocCard title="Draft proposal" inputId="prop" doc={proposal} onChange={onProposal} onUpload={(f, el) => onUpload('proposal', f, el)}>
          <select className="field" id="prop-sample" aria-label="Load a sample proposal" value={sampleId || ''} onChange={(e) => onSample(e.target.value)}>
            {!sampleId && <option value="">Edited text</option>}
            {SAMPLES.map((s) => (
              <option key={s.id} value={s.id}>{s.label}</option>
            ))}
          </select>
        </DocCard>
      </div>

      {notice && <p className="notice docs-notice">{notice}</p>}
    </section>
  )
}
