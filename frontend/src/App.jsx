import { useCallback, useEffect, useMemo, useState } from 'react'
import InputView from './components/InputView.jsx'
import CriteriaView, { COLUMNS } from './components/CriteriaView.jsx'
import RunView from './components/RunView.jsx'
import ResultView from './components/ResultView.jsx'
import SourcePane from './components/SourcePane.jsx'
import { CitationContext } from './components/Citation.jsx'
import { RFP, SAMPLES, matchSample, sampleById } from './data/samples.js'
import { norm } from './lib/markdown.js'
import { analyseRfp, scoreProposal } from './api/review.js'

const firstSample = SAMPLES[0]

// Ba man co noi dung; hai man tien trinh nam giua nen khong co trong thanh nay.
const FLOW = [['input', 'Documents'], ['criteria', 'Criteria'], ['result', 'Result']]

/** Luong mot chieu, ba man co noi dung: tai lieu -> tieu chi -> ket qua.
 *  Giua moi buoc la mot man tien trinh, vi ca hai agent deu mat thoi gian.
 *  Nguoi dung khong sua tieu chi: RFP Analyst chot mua ky. */
export default function App() {
  const [stage, setStage] = useState('input') // input | analysing | criteria | scoring | result | error
  const [rfp, setRfp] = useState({ ...RFP })
  const [proposal, setProposal] = useState({ name: firstSample.name, text: firstSample.text })
  // Bat dau rong: hai buoc sau chi mo khi da co du lieu that cua lan chay nay.
  const [analysis, setAnalysis] = useState(null)
  const [criteria, setCriteria] = useState([])
  // Ban goc tu RFP Analyst, de nut "Reset to the RFP suggestion" quay ve duoc.
  const [suggested, setSuggested] = useState([])
  const [run, setRun] = useState({ data: null, source: null })
  const [notice, setNotice] = useState(null)
  const [warnings, setWarnings] = useState([])
  const [citation, setCitation] = useState(null)
  const [tab, setTab] = useState('prop')
  const [drawer, setDrawer] = useState(false)
  const [wide, setWide] = useState(() => window.matchMedia('(min-width: 1180px)').matches)

  const sample = matchSample(rfp.text, proposal.text)
  const sampleId = sample ? sample.id : null
  const docked = wide && stage === 'result'
  const RUN_FLOOR = 3400

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

  /** Giu man tien trinh du lau de doc duoc, ke ca khi backend tra loi ngay. */
  const withFloor = async (work) => {
    const started = Date.now()
    const out = await work()
    const floor = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : RUN_FLOOR
    const left = floor - (Date.now() - started)
    if (left > 0) await new Promise((r) => setTimeout(r, left))
    return out
  }

  const startAnalysis = async (docs) => {
    const useRfp = docs?.rfp || rfp
    const useProposal = docs?.proposal || proposal
    setStage('analysing')
    setCitation(null)
    window.scrollTo({ top: 0 })
    const stored = matchSample(useRfp.text, useProposal.text)
    setWarnings([])
    try {
      const data = await withFloor(() => analyseRfp({ rfp: useRfp }))
      setAnalysis(data.rfp_analysis)
      setCriteria(data.confirmed_criteria)
      setSuggested(data.confirmed_criteria)
      setWarnings(data.warnings || [])
      setRun({ data: null, source: 'api' })
      setStage('criteria')
    } catch (err) {
      if (stored) {
        await withFloor(async () => null)
        setAnalysis(stored.result.rfp_analysis)
        setCriteria(stored.result.confirmed_criteria)
        setSuggested(stored.result.confirmed_criteria)
        setRun({ data: stored.result, source: 'sample', error: err.message })
        setStage('criteria')
      } else {
        setRun({ data: null, source: null, error: err.message })
        setStage('error')
      }
    }
  }

  const startScoring = async () => {
    setStage('scoring')
    window.scrollTo({ top: 0 })
    const stored = matchSample(rfp.text, proposal.text)
    try {
      const weightOf = (c) => COLUMNS.find((col) => col.id === c.recommended_priority)?.weight ?? 2
      const confirmed = criteria.map((c) => ({ ...c, weight: weightOf(c) }))
      const scoring = await withFloor(() => scoreProposal({
        rfp, proposal, rfp_analysis: analysis, confirmed_criteria: confirmed,
      }))
      setWarnings((w) => [...w, ...(scoring.warnings || [])])
      setRun({ data: { meta: { proposal_name: proposal.name }, rfp_analysis: analysis, confirmed_criteria: criteria, scoring }, source: 'api' })
      setStage('result')
    } catch (err) {
      if (stored) {
        await withFloor(async () => null)
        setRun({ data: stored.result, source: 'sample', error: err.message })
        setStage('result')
      } else {
        setRun({ data: null, source: null, error: err.message })
        setStage('error')
      }
    }
  }

  const analysisSteps = useMemo(() => ([
    { title: 'Reading the RFP', detail: 'Every requirement and constraint, in order', result: 'Requirements extracted' },
    { title: 'Marking hard constraints', detail: 'Things that cannot be traded away', result: 'Constraints marked' },
    { title: 'Setting the criteria', detail: 'Base rubric plus anything this RFP adds', result: 'Criteria weighted' },
  ]), [])

  const scoringSteps = useMemo(() => {
    const sections = (proposal.text.match(/^##\s/gm) || []).length
    return [
      { title: 'Reading the proposal', detail: `${sections} sections`, result: `${sections} sections mapped` },
      { title: 'Checking each requirement', detail: 'Addressed, vague, missing or contradicted', result: 'Requirements checked' },
      { title: 'Scoring each criterion', detail: `${criteria.length} criteria with their weights`, result: `${criteria.length} criteria scored` },
      { title: 'Verifying every quote', detail: 'A finding without a real quote is dropped', result: 'Quotes verified' },
    ]
  }, [proposal.text, criteria.length])

  const flowIndex = { input: 0, analysing: 0, criteria: 1, scoring: 1, result: 2, error: 0 }[stage]


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
        <nav className="flow" aria-label="Steps">
          {FLOW.map(([id, label], i) => {
            const reachable = id === 'input'
              || (id === 'criteria' && criteria.length > 0)
              || (id === 'result' && Boolean(run.data))
            const busy = stage === 'analysing' || stage === 'scoring'
            return (
              <button
                type="button" key={id} className="flow-step"
                title={reachable ? undefined : id === 'criteria' ? 'Run the review first' : 'No result yet'}
                data-state={i < flowIndex ? 'done' : i === flowIndex ? 'now' : 'next'}
                disabled={!reachable || busy}
                aria-current={i === flowIndex ? 'step' : undefined}
                onClick={() => { setStage(id); window.scrollTo({ top: 0 }) }}
              >
                {label}
              </button>
            )
          })}
        </nav>
        <div className="meta">{sampleId ? 'Fictional sample data' : 'Your documents'}</div>
      </header>

      <main className="wrap">
        {stage === 'input' && (
          <InputView
            rfp={rfp} proposal={proposal} sampleId={sampleId} notice={notice}
            onRfp={(text) => setRfp(() => ({ name: norm(text) === norm(RFP.text) ? RFP.name : 'Pasted RFP', text }))}
            onProposal={(text) => setProposal(() => {
              const match = SAMPLES.find((x) => norm(x.text) === norm(text))
              return { name: match ? match.name : 'Pasted proposal', text }
            })}
            onSample={(id) => loadSample(id)}
            onUpload={upload}
            onRun={() => startAnalysis()}
          />
        )}

        {stage === 'analysing' && <RunView steps={analysisSteps} title="Reading the RFP" subtitle={rfp.name} />}
        {stage === 'scoring' && <RunView steps={scoringSteps} title={proposal.name} subtitle={`against ${rfp.name}`} />}

        {stage === 'criteria' && (
          <CriteriaView
            analysis={analysis} criteria={criteria}
            onChange={setCriteria}
            onReset={() => setCriteria(suggested)}
            onRun={startScoring}
            warnings={warnings}
          />
        )}

        {stage === 'error' && (
          <div className="run-view">
            <div className="run-card">
              <h1>No review yet</h1>
              <p className="lede">{run.error}</p>
              <div className="hero-actions">
                <button type="button" className="btn btn-primary" onClick={() => startAnalysis()}>Try again</button>
                <button type="button" className="btn" onClick={() => {
                  const s = loadSample(firstSample.id)
                  startAnalysis({ rfp: { ...RFP }, proposal: { name: s.name, text: s.text } })
                }}>Load a sample instead</button>
              </div>
            </div>
          </div>
        )}

        {stage === 'result' && run.data && (
          <ResultView
            result={run.data} source={run.source} error={run.error} sampleId={sampleId} warnings={warnings}
            onSample={(id) => {
              const s = loadSample(id)
              startAnalysis({ rfp: { ...RFP }, proposal: { name: s.name, text: s.text } })
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
