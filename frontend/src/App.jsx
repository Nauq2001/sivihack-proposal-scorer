import { useState } from 'react'

export default function App() {
  const [prompt, setPrompt] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleAsk() {
    setLoading(true)
    setError('')
    setAnswer('')
    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      })
      if (!res.ok) throw new Error(`Backend loi: ${res.status}`)
      const data = await res.json()
      setAnswer(data.answer)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 640, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>SiviHack Project</h1>
      <p>Demo ket noi frontend &rarr; backend &rarr; AI API. Thay giao dien nay bang UI that cua de bai.</p>

      <textarea
        rows={4}
        style={{ width: '100%', padding: 8 }}
        placeholder="Nhap thu prompt de test AI..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />

      <button onClick={handleAsk} disabled={loading || !prompt} style={{ marginTop: 8, padding: '8px 16px' }}>
        {loading ? 'Dang goi AI...' : 'Gui'}
      </button>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {answer && (
        <div style={{ marginTop: 16, padding: 12, background: '#f4f4f4', borderRadius: 8 }}>
          <strong>Tra loi:</strong>
          <p>{answer}</p>
        </div>
      )}
    </div>
  )
}
