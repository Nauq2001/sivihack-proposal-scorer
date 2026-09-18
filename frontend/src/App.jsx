import { useCallback, useEffect, useMemo, useState } from 'react'
import InputView from './components/InputView.jsx'
import RunView from './components/RunView.jsx'
import ResultView from './components/ResultView.jsx'
import SourcePane from './components/SourcePane.jsx'
import { CitationContext } from './components/Citation.jsx'
import { RFP, SAMPLES, matchSample, sampleById } from './data/samples.js'
import { reviewProposal } from './api/review.js'

const firstSample = SAMPLES[0]

/** Luồng thẳng một chiều: nhập tài liệu -> chạy -> đọc kết quả.
 *  Không có bước chỉnh tiêu chí: RFP Analyst chốt tiêu chí và trọng số. */
export default function App() {
  const [stage, setStage] = useState('result') // input | running | result | error
  const [rfp, setRfp] = useState({ ...RFP })
  const [proposal, setProposal] = useState({ name: firstSample.name, text: firstSample.text })
  const [run, setRun] = useState({ data: firstSample.result, source: 'sample' })
  const [notice, setNotice] = useState(null)
  const [citation, setCitation] = useState(null)
  const [tab, setTab] = useState('prop')
  const [drawer, setDrawer] = useState(false)
  const [wide, setWide] = useState(() => window.matchMedia('(min-width: 1180px)').matches)

  const sample = matchSample(rfp.text, proposal.text)
  const sampleId = sample ? sample.id : null
  const docked = wide && stage === 'result'

  useEffect(() => {
    const mq = window.matchMedia('(min-width: 1180px)')
    const onChange = (e) => setWide(e.matches)
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])

  useEffect(() => {
    document.body.classList.toggle('dock', docked)
    if (docked) setDrawer(false)
  }, [docked])

  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') setDrawer(false) }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [])

  const openCitation = useCallback((c) => {
    setCitation(c)
    setTab(c.source === 'rfp' ? 'rfp' : 'prop')
    if (!(window.matchMedia('(min-width: 1180px)').matches && stage === 'result')) setDrawer(true)
  }, [stage])

  const loadSample = (id) => {
    const s = sampleById(id)
    if (!s) return null
    setRfp({ ...RFP })
    setProposal({ name: s.name, text: s.text })
    setNotice(null)
    return s
  }

  const upload = (which, file, input) => {
    if (!file) return
    if (/\.pdf$/i.test(file.name)) {
      setNotice(`PDF import is not wired up yet, so ${file.name} was not loaded. Paste the text instead.`)
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

  // Cac buoc chay phai kip hien ra, ke ca khi backend tra loi ngay lap tuc.
  const RUN_FLOOR_MS = 3600

  const runReview = async (docs) => {
    const useRfp = docs?.rfp || rfp
    const useProposal = docs?.proposal || proposal
    const started = Date.now()
    setStage('running')
    setCitation(null)
    window.scrollTo({ top: 0 })

    const settle = async (next) => {
      const floor = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : RUN_FLOOR_MS
      const left = floor - (Date.now() - started)
      if (left > 0) await new Promise((r) => setTimeout(r, left))
      next()
    }

    try {
      const data = await reviewProposal({ rfp: useRfp, proposal: useProposal })
      await settle(() => { setRun({ data, source: 'api' }); setStage('result') })
    } catch (err) {
      const stored = matchSample(useRfp.text, useProposal.text)
      if (stored) {
        await settle(() => { setRun({ data: stored.result, source: 'sample', error: err.message }); setStage('result') })
      } else {
        await settle(() => { setRun({ data: null, source: null, error: err.message }); setStage('error') })
      }
    }
  }

  const steps = useMemo(() => {
    const sections = (proposal.text.match(/^##\s/gm) || []).length
    const data = run.data
    return [
      { title: 'Reading the RFP', detail: 'Pulling out every requirement and constraint',
        result: data ? `${data.rfp_analysis.requirements.length} requirements, ${data.rfp_analysis.requirements.filter((r) => r.is_hard_constraint).length} hard constraints` : 'Requirements extracted' },
      { title: 'Setting the criteria', detail: 'Base rubric plus anything this RFP adds',
        result: data ? `${data.confirmed_criteria.length} criteria weighted` : 'Criteria weighted' },
      { title: 'Reading the proposal', detail: `${sections} sections`, result: `${sections} sections mapped` },
      { title: 'Scoring against each requirement', detail: 'Match, vague, missing or contradicted',
        result: data ? `${data.evaluation.requirements.filter((r) => r.status !== 'met').length} gaps found` : 'Gaps found' },
      { title: 'Checking every quote', detail: 'A finding without a real quote is dropped',
        result: data ? `${data.evaluation.findings.length} findings kept` : 'Findings verified' },
    ]
  }, [proposal.text, run.data])

  return (
    <CitationContext.Provider value={openCitation}>
      <header className="topbar">
        <button type="button" className="brand" onClick={() => setStage('input')}>
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M5 3h9l5 5v13H5z" fill="var(--surface)" stroke="var(--ink)" strokeWidth="1.6" strokeLinejoin="round" />
            <path d="M14 3v5h5" stroke="var(--ink)" strokeWidth="1.6" strokeLinejoin="round" />
            <path d="M8.5 14.5l2.2 2.2 4.8-5" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Proposal Scorer
        </button>
        <div className="flow" aria-label="Progress">
          {['Documents', 'Review', 'Result'].map((label, i) => {
            const index = stage === 'input' ? 0 : stage === 'running' ? 1 : 2
            return <span key={label} className="flow-step" data-state={i < index ? 'done' : i === index ? 'now' : 'next'}>{label}</span>
          })}
        </div>
        <div className="meta">{sampleId ? 'Fictional sample data' : 'Your documents'}</div>
      </header>

      <main className="wrap">
        {stage === 'input' && (
          <InputView
            rfp={rfp} proposal={proposal} sampleId={sampleId} notice={notice}
            onRfp={(text) => setRfp((d) => ({ ...d, text }))}
            onProposal={(text) => setProposal((d) => ({ ...d, text }))}
            onSample={(id) => loadSample(id)}
            onUpload={upload}
            onRun={() => runReview()}
          />
        )}

        {stage === 'running' && <RunView steps={steps} rfpName={rfp.name} proposalName={proposal.name} />}

        {stage === 'error' && (
          <div className="run-view">
            <div className="run-card">
              <h1>No review yet</h1>
              <p className="lede">{run.error}</p>
              <div className="hero-actions">
                <button type="button" className="btn btn-primary" onClick={() => runReview()}>Try again</button>
                <button type="button" className="btn" onClick={() => {
                  const s = loadSample(firstSample.id)
                  runReview({ rfp: { ...RFP }, proposal: { name: s.name, text: s.text } })
                }}>Load a sample instead</button>
              </div>
            </div>
          </div>
        )}

        {stage === 'result' && run.data && (
          <ResultView
            result={run.data} source={run.source} error={run.error} sampleId={sampleId}
            onSample={(id) => {
              const s = loadSample(id)
              runReview({ rfp: { ...RFP }, proposal: { name: s.name, text: s.text } })
            }}
            onRestart={() => { setStage('input'); window.scrollTo({ top: 0 }) }}
          />
        )}
      </main>

      {drawer && !docked && <div id="scrim" onClick={() => setDrawer(false)} />}
      <SourcePane
        rfp={rfp} proposal={proposal} tab={tab} onTab={setTab} citation={citation}
        docked={docked} open={drawer} onClose={() => setDrawer(false)}
      />
    </CitationContext.Provider>
  )
}
