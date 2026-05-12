import { useState } from 'react'

const apiBase = 'http://127.0.0.1:8000'

function App() {
  const [file, setFile] = useState(null)
  const [fileInputKey, setFileInputKey] = useState(Date.now())
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFileChange = (event) => {
    setFile(event.target.files?.[0] || null)
    setResult(null)
    setError('')
  }

  const clearText = () => {
    setText('')
    setResult(null)
    setError('')
  }

  const clearFile = () => {
    setFile(null)
    setResult(null)
    setError('')
    setFileInputKey(Date.now())
  }

  const clearAll = () => {
    setText('')
    setFile(null)
    setResult(null)
    setError('')
    setFileInputKey(Date.now())
  }

  const submitText = async () => {
    setError('')
    setLoading(true)
    try {
      const response = await fetch(`${apiBase}/process-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })
      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Unable to process text. Check backend status.')
    } finally {
      setLoading(false)
    }
  }

  const submitFile = async () => {
    if (!file) {
      setError('Please select a file first.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await fetch(`${apiBase}/process-file`, {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Unable to process file. Check backend status.')
    } finally {
      setLoading(false)
    }
  }

  const formatFieldKey = (key) => key.replace(/([A-Z])/g, ' $1').replace(/^./, (c) => c.toUpperCase())

  const formatBytes = (bytes) => {
    if (!bytes) return ''
    const k = 1024
    const sizes = ['B', 'KB', 'MB']
    const i = Math.min(Math.floor(Math.log(bytes) / Math.log(k)), sizes.length - 1)
    return `${parseFloat((bytes / k ** i).toFixed(1))} ${sizes[i]}`
  }

  return (
    <div className="app-container">
      <header>
        <div className="hero-card">
          <div>
            <p className="eyebrow">Insurance claim intake</p>
            <h1>Capture FNOL data instantly</h1>
            <p className="hero-copy">
              Paste a claim report or upload a file to extract policy details automatically and route the claim to the right queue.
            </p>
          </div>
          <div className="hero-pill">Fast, clear, and visual</div>
        </div>
      </header>

      <section className="panel intro-panel">
        <div>
          <p className="section-label">How it works</p>
          <h2>Quick claim intake in three steps</h2>
          <ul className="steps-list">
            <li>Paste claim text or upload a supported file.</li>
            <li>Process the document to extract fields automatically.</li>
            <li>Review the recommended route and missing field checklist.</li>
          </ul>
        </div>

        <div className="intro-actions">
          <button className="ghost" onClick={clearAll}>
            Clear all inputs
          </button>
          <div className="pill-box">
            <strong>Supported formats</strong>
            <span>.pdf</span>
            <span>.txt</span>
          </div>
        </div>
      </section>

      <div className="panels-grid">
        <section className="panel card-panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">Text mode</p>
              <h2>Paste claim text</h2>
            </div>
            <button className="ghost small" onClick={clearText} disabled={!text && !result}>
              Clear text
            </button>
          </div>

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste FNOL document text here"
            rows={12}
          />

          <div className="panel-actions">
            <button className="primary" onClick={submitText} disabled={loading || !text.trim()}>
              Process Text
            </button>
          </div>
        </section>

        <section className="panel card-panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">File mode</p>
              <h2>Upload a document</h2>
            </div>
            <button className="ghost small" onClick={clearFile} disabled={!file && !result}>
              Clear file
            </button>
          </div>

          <label className="file-picker">
            <div className="file-picker-icon" aria-hidden="true">📁</div>
            <div className="file-picker-text">
              <span className="file-picker-title">{file ? 'File selected' : 'Choose a claim file'}</span>
              <span className="file-picker-subtitle">
                {file ? file.name : 'PDF and TXT files supported'}
              </span>
            </div>
            <input key={fileInputKey} type="file" accept=".pdf,.txt" onChange={handleFileChange} />
          </label>
          {file && (
            <div className="file-details">
              <span className="file-detail-pill">{formatBytes(file.size)}</span>
              <span className="file-detail-pill">{file.type || 'Document'}</span>
            </div>
          )}

          <div className="panel-actions">
            <button className="secondary" onClick={submitFile} disabled={loading || !file}>
              Process File
            </button>
          </div>
        </section>
      </div>

      {error && <div className="notification error">{error}</div>}
      {loading && <div className="notification loading">Processing…</div>}

      {result && (
        <section className="panel result-panel">
          <div className="result-header">
            <div>
              <p className="section-label">Result</p>
              <h2>Claim summary</h2>
            </div>
            <div className="result-meta">
              <button className="ghost small" onClick={() => setResult(null)}>
                Clear output
              </button>
              <div className={`route-badge route-${result.recommendedRoute.replace(/\s+/g, '-').toLowerCase()}`}>
                {result.recommendedRoute}
              </div>
            </div>
          </div>

          <div className="highlight-grid">
            <div className="highlight-card">
              <p className="highlight-label">Fields extracted</p>
              <h3>{Object.values(result.extractedFields).filter((value) => value && value !== 'unknown').length}</h3>
            </div>
            <div className="highlight-card">
              <p className="highlight-label">Missing fields</p>
              <h3>{result.missingFields.length}</h3>
            </div>
            <div className="highlight-card">
              <p className="highlight-label">Route selected</p>
              <h3>{result.recommendedRoute}</h3>
            </div>
          </div>

          <div className="result-grid">
            <div className="result-card">
              <p className="card-title">Reasoning</p>
              <p>{result.reasoning}</p>
            </div>
            <div className="result-card">
              <p className="card-title">Missing fields</p>
              {result.missingFields.length ? (
                <ul>
                  {result.missingFields.map((field) => (
                    <li key={field}>{formatFieldKey(field)}</li>
                  ))}
                </ul>
              ) : (
                <p className="none-text">No missing fields</p>
              )}
            </div>
          </div>

          <div className="fields-grid">
            {Object.entries(result.extractedFields).map(([key, value]) => (
              <div className="field-item" key={key}>
                <span className="field-name">{formatFieldKey(key)}</span>
                <span className="field-value">{value || '—'}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

export default App
