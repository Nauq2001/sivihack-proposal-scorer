import { useCallback, useEffect, useMemo, useState } from 'react'
import DocumentsStep from './components/DocumentsStep.jsx'
import CriteriaStep from './components/CriteriaStep.jsx'
import ReviewStep from './components/ReviewStep.jsx'
import RunProgress from './components/RunProgress.jsx'
import SourcePane from './components/SourcePane.jsx'
import { CitationContext } from './components/Citation.jsx'
import { RFP, SAMPLES, matchSample, sampleById } from './data/samples.js'
import { reviewProposal } from './api/review.js'
import { CRITERIA, DEFAULT_LEVELS, criteriaPayload, weightNote } from './lib/scoring.js'

const STEPS = [
  ['docs', 'Documents'],
  ['criteria', 'Criteria'],
  ['review', 'Review'],
]

const firstSample = SAMPLES[0]

export default function App() {
  const [step, setStep] = useState('review')
  const [rfp, setRfp] = useState({ ...RFP })
  const [proposal, setProposal] = useState({ name: firstSample.name, text: firstSample.text })
  const [levels, setLevels] = useState(DEFAULT_LEVELS)
  // run: {state: 'done'|'running'|'error', data, source: 'api'|'sample', error}
  const [run, setRun] = useState({ state: 'done', data: firstSample.result, source: 'sample' })
  const [citation, setCitation] = useState(null)
  const [tab, setTab] = useState('prop')
  const [drawer, setDrawer] = useState(false)
  const [notice, setNotice] = useState(null)
  const [wide, setWide] = useState(() => window.matchMedia('(min-width: 1100px)').matches)

  const sample = matchSample(rfp.text, proposal.text)
  const sampleId = sample ? sample.id : null
  const docked = wide && step === 'review'

  useEffect(() => {
    const mq = window.matchMedia('(min-width: 1100px)')
    const onChange = (e) => setWide(e.matches)
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])

  useEffect(() => {
    document.body.classList.toggle('dock', docked)
    if (docked) setDrawer(false)
  }, [docked])

  const openCitation = useCallback((c) => {
    setCitation(c)
    setTab(c.source === 'rfp' ? 'rfp' : 'prop')
    if (!(window.matchMedia('(min-width: 1100px)').matches && step === 'review')) setDrawer(true)
  }, [step])

  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') setDrawer(false) }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [])

  const go = (next) => {
    setStep(next)
    window.scrollTo({ top: 0 })
  }

  const loadSample = (id) => {
    const s = sampleById(id)
    if (!s) return
    setRfp({ ...RFP })
    setProposal({ name: s.name, text: s.text })
    setNotice(null)
    return s
  }

  const upload = (which, file, input) => {
    if (!file) return
    if (/\.pdf$/i.test(file.name)) {
      setNotice(`PDF import isn’t supported yet, so ${file.name} was not loaded. Paste the text instead.`)
      input.value = ''
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      const doc = { name: file.name, text: String(reader.result) }
      if (which === 'rfp') setRfp(doc); else setProposal(doc)
      setNotice(null)
    }
    reader.readAsText(file)
    input.value = ''
  }

  const runReview = async (docs) => {
    const useRfp = docs?.rfp || rfp
    const useProposal = docs?.proposal || proposal
    setRun({ state: 'running' })
    setCitation(null)
    go('review')
    try {
      const data = await reviewProposal({ rfp: useRfp, proposal: useProposal, criteria: criteriaPayload(levels) })
      setRun({ state: 'done', data, source: 'api' })
    } catch (err) {
      const stored = matchSample(useRfp.text, useProposal.text)
      if (stored) setRun({ state: 'done', data: stored.result, source: 'sample', error: err.message })
      else setRun({ state: 'error', error: err.message })
    }
  }

  const runSteps = useMemo(() => ([
    ['Reading the RFP', 'Pulling out every explicit requirement'],
    ['Mapping the proposal', `${(proposal.text.match(/^##\s/gm) || []).length} sections in ${proposal.name}`],
    ['Checking each requirement against the proposal', 'Matches, vague wording and contradictions'],
    [`Scoring ${CRITERIA.length} criteria`, weightNote(levels, run.data?.suggested_weights)],
    ['Writing suggested fixes', 'One per gap, with citations'],
  ]), [proposal.text, proposal.name, levels, run.data])

  return (
    <CitationContext.Provider value={openCitation}>
      <header className="topbar">
        <div className="brand">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M5 3h9l5 5v13H5z" fill="var(--surface)" stroke="var(--ink)" strokeWidth="1.6" strokeLinejoin="round" />
            <path d="M14 3v5h5" stroke="var(--ink)" strokeWidth="1.6" strokeLinejoin="round" />
            <path d="M8.5 14.5l2.2 2.2 4.8-5" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Proposal Scorer
        </div>
        <nav className="steps" aria-label="Review steps">
          {STEPS.map(([id, label], i) => (
            <button type="button" className="step" key={id} aria-current={step === id ? 'step' : 'false'} onClick={() => go(id)}>
              <span className="n">{i + 1}</span>
              {label}
            </button>
          ))}
        </nav>
        <div className="meta">{sampleId ? 'Fictional sample data' : 'Your documents'}</div>
      </header>

      <main className="wrap">
        {step === 'docs' && (
          <DocumentsStep
            rfp={rfp}
            proposal={proposal}
            sampleId={sampleId}
            notice={notice}
            onRfp={(text) => setRfp((d) => ({ ...d, text }))}
            onProposal={(text) => setProposal((d) => ({ ...d, text }))}
            onSample={loadSample}
            onUpload={upload}
            onGo={go}
            onRun={() => runReview()}
          />
        )}

        {step === 'criteria' && (
          <CriteriaStep
            levels={levels}
            suggested={run.data?.suggested_weights}
            priorities={run.data?.client_priorities || []}
            onLevel={(id, value) => setLevels((l) => ({ ...l, [id]: value }))}
            onLevels={setLevels}
            onGo={go}
            onRun={() => runReview()}
          />
        )}

        {step === 'review' && (
          <div className="review-main">
            {run.state === 'running' && <RunProgress steps={runSteps} rfpName={rfp.name} proposalName={proposal.name} />}

            {run.state === 'error' && (
              <div className="panel run">
                <h2>No review yet</h2>
                <p>{run.error}</p>
                <div className="actions">
                  <button type="button" className="btn btn-primary" onClick={() => runReview()}>Try again</button>
                  <button
                    type="button"
                    className="btn"
                    onClick={() => { const s = loadSample(firstSample.id); runReview({ rfp: { ...RFP }, proposal: { name: s.name, text: s.text } }) }}
                  >
                    Load a sample instead
                  </button>
                </div>
              </div>
            )}

            {run.state === 'done' && (
              <ReviewStep
                result={run.data}
                levels={levels}
                sampleId={sampleId}
                source={run.source}
                error={run.error}
                onSample={(id) => { const s = loadSample(id); runReview({ rfp: { ...RFP }, proposal: { name: s.name, text: s.text } }) }}
                onRun={() => runReview()}
                onGo={go}
              />
            )}
          </div>
        )}
      </main>

      {drawer && !docked && <div id="scrim" onClick={() => setDrawer(false)} />}
      <SourcePane
        rfp={rfp}
        proposal={proposal}
        tab={tab}
        onTab={setTab}
        citation={citation}
        docked={docked}
        open={drawer}
        onClose={() => setDrawer(false)}
      />
    </CitationContext.Provider>
  )
}
