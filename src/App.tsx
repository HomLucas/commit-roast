import { useState, useRef } from 'react'
import { fetchCommits } from './github'
import { analyzePersonality, type PersonalityResult, type ProviderType } from './api'
import html2canvas from 'html2canvas'
import Card from './Card'

const PROVIDERS: { value: ProviderType; label: string; getKeyUrl: string }[] = [
  { value: 'openai', label: 'OpenAI', getKeyUrl: 'https://platform.openai.com/api-keys' },
  { value: 'gemini', label: 'Gemini', getKeyUrl: 'https://aistudio.google.com/apikey' },
  { value: 'anthropic', label: 'Anthropic', getKeyUrl: 'https://console.anthropic.com/keys' },
  { value: 'deepseek', label: 'DeepSeek', getKeyUrl: 'https://platform.deepseek.com/api_keys' },
]

export default function App() {
  const [username, setUsername] = useState('')
  const [provider, setProvider] = useState<ProviderType>('openai')
  const [apiKey, setApiKey] = useState('')
  const [githubToken, setGithubToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PersonalityResult | null>(null)
  const [error, setError] = useState('')
  const [commitsCount, setCommitsCount] = useState(0)
  const cardRef = useRef<HTMLDivElement>(null)

  const selected = PROVIDERS.find((p) => p.value === provider)!

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setResult(null)
    const u = username.trim()
    const k = apiKey.trim()
    if (!u) { setError('Enter a GitHub username'); return }
    if (!k) { setError('Enter your API key'); return }
    setLoading(true)
    try {
      const commits = await fetchCommits(u, githubToken.trim() || undefined)
      setCommitsCount(commits.length)
      const personality = await analyzePersonality(provider, k, commits)
      setResult(personality)
    } catch (err: any) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const downloadCard = async () => {
    if (!cardRef.current) return
    const canvas = await html2canvas(cardRef.current, {
      backgroundColor: '#0a0a0f', scale: 2, useCORS: true,
    })
    const link = document.createElement('a')
    link.download = `${username}-commitroast.png`
    link.href = canvas.toDataURL()
    link.click()
  }

  return (
    <div className="min-h-screen flex flex-col items-center px-4 sm:px-6 py-8 sm:py-16">
      {/* Header */}
      <div className="text-center mb-8 sm:mb-12 max-w-lg mx-auto">
        <div className="text-4xl sm:text-5xl mb-3">💾</div>
        <h1 className="font-retro text-base sm:text-lg text-fuchsia-400 mb-3 glitch tracking-wide">
          COMMIT ROAST
        </h1>
        <p className="text-cyan-300/80 font-pixel text-base sm:text-lg leading-relaxed">
          paste a github username. get your coding personality analyzed by ai.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-3">
        <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="GitHub username"
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:outline-none focus:border-fuchsia-500/50 focus:ring-1 focus:ring-fuchsia-500/20 transition-all text-sm"
          />
          <input
            value={githubToken}
            onChange={(e) => setGithubToken(e.target.value)}
            type="password"
            placeholder="GitHub token (optional — 5,000 req/hr instead of 60)"
            className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-all text-xs"
          />
          <div className="flex gap-2">
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value as ProviderType)}
            className="shrink-0 px-3 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:outline-none focus:border-cyan-500/50"
          >
            {PROVIDERS.map((p) => (
              <option key={p.value} value={p.value} className="bg-[#0a0a0f]">{p.label}</option>
            ))}
          </select>
          <input
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            type="password"
            placeholder="API key"
            className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-gray-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-all text-sm"
          />
        </div>
        <p className="text-gray-600 text-xs text-center">
          <a href={selected.getKeyUrl} target="_blank" rel="noopener noreferrer" className="text-cyan-500/60 hover:text-cyan-400 underline underline-offset-2">
            get a {selected.label} key
          </a>
        </p>
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-fuchsia-600 to-cyan-600 text-white font-semibold text-sm hover:from-fuchsia-500 hover:to-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-lg shadow-fuchsia-500/10"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              analyzing...
            </span>
          ) : (
            'Roast my commits'
          )}
        </button>
      </form>

      {/* Security notice */}
      <p className="text-gray-600 text-xs text-center mt-6 max-w-sm leading-relaxed">
        your key is sent directly to {selected.label} from your browser. never stored or logged.
        {' '}<a href="https://github.com/HomLucas/commit-roast" target="_blank" rel="noopener noreferrer" className="text-cyan-500/60 hover:text-cyan-400 underline underline-offset-2">source</a>
      </p>

      {/* Error */}
      {error && (
        <div className="text-red-400 text-sm mt-6 text-center max-w-sm bg-red-500/5 border border-red-500/10 rounded-xl px-5 py-3">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <p className="text-cyan-300/60 text-sm mt-6 animate-pulse">reading commit history...</p>
      )}

      {/* Result */}
      {result && (
        <div className="flex flex-col items-center gap-5 w-full max-w-lg mt-8">
          <div ref={cardRef} className="w-full">
            <Card username={username} result={result} />
          </div>
          <div className="flex gap-3">
            <button onClick={downloadCard} className="px-5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-cyan-300 hover:bg-white/10 transition-all">
              Download
            </button>
            <button onClick={() => { setResult(null); setUsername(''); setApiKey('') }} className="px-5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-gray-400 hover:bg-white/10 transition-all">
              Try another
            </button>
          </div>
          <p className="text-gray-500 text-xs">
            analyzed {commitsCount} commits via {selected.label}
          </p>
        </div>
      )}

      {/* Footer */}
      <p className="text-gray-700 text-xs mt-auto pt-16 pb-6 text-center">
        no data stored. open source on{' '}
        <a href="https://github.com/HomLucas/commit-roast" target="_blank" rel="noopener noreferrer" className="text-cyan-500/60 hover:text-cyan-400 underline underline-offset-2">github</a>
      </p>
    </div>
  )
}
