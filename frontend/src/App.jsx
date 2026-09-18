import { useCallback, useEffect, useMemo, useState } from 'react'
import InputView from './components/InputView.jsx'
import CriteriaView, { COLUMNS } from './components/CriteriaView.jsx'
import RunView from './components/RunView.jsx'
import ResultView from './components/ResultView.jsx'
import SourcePane from './components/SourcePane.jsx'
import { CitationContext } from './components/Citation.jsx'
import { RFP, SAMPLES, matchSample, sampleById } from './data/samples.js'
import { norm } from './lib/markdown.js'
import { CONVERTIBLE, PLAIN_TEXT, analyseRfp, confirmCriteria, convertFile, extensionOf, scoreProposal } from './api/review.js'

const firstSample = SAMPLES[0]

/** Tieu chi nguoi dung tu them phai co packet rieng truoc khi gui di cham.
 *
 *  Khong co packet thi prompt cua Scoring Agent chi thay "(none)" o phan huong
 *  dan va ghi chu, mat luon rao chan `USER_DEFINED_NOT_RFP`: tieu chi tu them
 *  khong phai yeu cau cua RFP, khong duoc bao cao nhu mot muc bi thieu.
 *
 *  Day dung la nhanh du phong cua `resolve_user_criterion` khi khong co
 *  resolver (agent/src/rfp_analyst/criteria.py) — lien ket de rong, ghi chu
 *  canh bao khong bia them nghia vu. */
function withUserPackets(analysis, confirmed) {
  const known = new Set((analysis.criterion_packets || []).map((p) => p.criterion_name))
  const added = confirmed
    .filter((c) => !known.has(c.name))
    .map((c) => ({
      criterion_name: c.name,
      origin: 'user',
      evaluation_guidance: [`Evaluate only this user-defined expectation: ${c.description}`],
      requirement_ids: [],
      source_refs: [],
      notes: [
        'USER_DEFINED_NOT_RFP: Score against the user’s description; do not report it as a missing RFP requirement.',
        'ENRICHMENT_FAILED: No verified RFP links were added; do not invent thresholds or obligations.',
      ],
    }))
  if (!added.length) return analysis
  return { ...analysis, criterion_packets: [...(analysis.criterion_packets || []), ...added] }
}

// Ba man co noi dung; hai man tien trinh nam giua nen khong co trong thanh nay.
const FLOW = [['input', 'Documents'], ['criteria', 'Criteria'], ['result', 'Result']]

const SESSION_KEY = 'proposal-scorer/run'

/** Mot lan chay ton khoang 30 giay va hai luot goi Gemini. Lo bam F5 giua buoi
 *  demo ma phai chay lai tu dau la mat trang. Chi luu trong tab dang mo: doi
 *  tai lieu khac thi khong keo theo ket qua cu. */
function loadSession() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function saveSession(state) {
  try {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(state))
  } catch {
    // Het cho hoac tab rieng tu — mat phien luu khong lam hong phien dang chay.
  }
}

/** Luong mot chieu, ba man co noi dung: tai lieu -> tieu chi -> ket qua.
 *  Giua moi buoc la mot man tien trinh, vi ca hai agent deu mat thoi gian.
 *  Nguoi dung khong sua tieu chi: RFP Analyst chot mua ky. */
export default function App() {
  const saved = loadSession()
  const [stage, setStage] = useState(saved?.stage || 'input') // input | analysing | criteria | scoring | result | error
  const [rfp, setRfp] = useState(saved?.rfp || { ...RFP })
  const [proposal, setProposal] = useState(saved?.proposal || { name: firstSample.name, text: firstSample.text })
  // Bat dau rong: hai buoc sau chi mo khi da co du lieu that cua lan chay nay.
  const [analysis, setAnalysis] = useState(saved?.analysis || null)
  const [criteria, setCriteria] = useState(saved?.criteria || [])
  // Ban goc tu RFP Analyst, de nut "Reset to the RFP suggestion" quay ve duoc.
  const [suggested, setSuggested] = useState(saved?.suggested || [])
  const [run, setRun] = useState(saved?.run || { data: null, source: null })
  const [notice, setNotice] = useState(null)
  const [converting, setConverting] = useState(null) // 'rfp' | 'proposal' khi dang doc file
  const [warnings, setWarnings] = useState(saved?.warnings || [])
  const [citation, setCitation] = useState(null)
  const [tab, setTab] = useState('prop')
  const [drawer, setDrawer] = useState(false)
  const [wide, setWide] = useState(() => window.matchMedia('(min-width: 1180px)').matches)

  const sample = matchSample(rfp.text, proposal.text)
  const sampleId = sample ? sample.id : null
  const docked = wide && stage === 'result'
  const RUN_FLOOR = 3400

  // Hai man tien trinh khong luu: tai lai giua chung thi khong co gi de tiep
  // tuc, quay ve man truoc do la dung hon.
  useEffect(() => {
    const resume = { analysing: 'input', scoring: 'criteria' }[stage] || stage
    saveSession({ stage: resume, rfp, proposal, analysis, criteria, suggested, run, warnings })
  }, [stage, rfp, proposal, analysis, criteria, suggested, run, warnings])

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

  const readAsText = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(new Error(`${file.name} could not be read.`))
    reader.readAsText(file)
  })

  /** PDF/DOCX/PPTX/anh di qua /v1/markitdown/convert; .md/.txt doc thang.
   *  Chuyen doi mat vai giay va co the hong, nen o nhap hien trang thai rieng. */
  const upload = async (which, file, input) => {
    if (input) input.value = ''
    if (!file) return
    const ext = extensionOf(file.name)
    const convertible = CONVERTIBLE.includes(ext)
    if (!convertible && !PLAIN_TEXT.includes(ext)) {
      setNotice(`${file.name} is not a format the reader can open. Use PDF, Word, PowerPoint, an image, or plain text.`)
      return
    }
    setNotice(null)
    setConverting(which)
    try {
      const text = convertible ? await convertFile(file) : await readAsText(file)
      if (!text.trim()) throw new Error(`Nothing could be read out of ${file.name}.`)
      const doc = { name: file.name, text }
      if (which === 'rfp') setRfp(doc); else setProposal(doc)
    } catch (err) {
      setNotice(err.message)
    } finally {
      setConverting(null)
    }
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

  /** Chot tieu chi. Buoc nay hong thi van cham duoc: dung danh sach nguoi dung
   *  da chon, kem packet du phong — giong het nhanh offline cua agent. */
  const confirmStep = async (edited) => {
    try {
      const out = await confirmCriteria({ rfp, rfp_analysis: analysis, criteria: edited })
      const notes = [...(out.warnings || [])]
      for (const m of out.merges || []) {
        notes.push(`“${m.added}” already existed as “${m.merged_into}”, so the two were scored as one.`)
      }
      setCriteria(out.confirmed_criteria)
      setAnalysis(out.rfp_analysis)
      return { confirmed: out.confirmed_criteria, sourceAnalysis: out.rfp_analysis, notes }
    } catch (err) {
      return {
        confirmed: edited,
        sourceAnalysis: withUserPackets(analysis, edited),
        notes: [`The criteria were used exactly as you set them (${err.message})`],
      }
    }
  }

  const startScoring = async () => {
    setStage('scoring')
    window.scrollTo({ top: 0 })
    const stored = matchSample(rfp.text, proposal.text)
    try {
      const weightOf = (c) => COLUMNS.find((col) => col.id === c.recommended_priority)?.weight ?? 2
      const edited = criteria.map((c) => ({ ...c, weight: weightOf(c) }))

      // Chot truoc, cham sau. Resolver chay o buoc chot nay, dung mot lan cho
      // ca danh sach — them tieu chi o man 2 khong ton lan goi model nao.
      const { confirmed, sourceAnalysis, notes } = await confirmStep(edited)
      const scoring = await withFloor(() => scoreProposal({
        rfp, proposal, rfp_analysis: sourceAnalysis, confirmed_criteria: confirmed,
      }))
      setWarnings((w) => [...w, ...notes, ...(scoring.warnings || [])])
      // `confirmed`, khong phai `criteria`: trang ket qua phai hien dung trong so
      // da dung de cham, tuc trong so cua cot nguoi dung chot.
      setRun({ data: { meta: { proposal_name: proposal.name }, rfp_analysis: analysis, confirmed_criteria: confirmed, scoring }, source: 'api' })
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
      { title: 'Locking the criteria', detail: 'Merging anything that overlaps, linking yours to the RFP', result: 'Criteria locked' },
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
            rfp={rfp} proposal={proposal} sampleId={sampleId} notice={notice} converting={converting}
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
            analysis={analysis} criteria={criteria} suggested={suggested}
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
