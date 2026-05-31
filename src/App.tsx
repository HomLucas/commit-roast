import { useState, useRef } from 'react'
import { fetchCommits } from './github'
import { analyzePersonality, type PersonalityResult } from './gemini'
import html2canvas from 'html2canvas'
import Card from './Card'

export default function App() {
  const [username, setUsername] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PersonalityResult | null>(null)
  const [error, setError] = useState('')
  const [commitsCount, setCommitsCount] = useState(0)
  const cardRef = useRef<HTMLDivElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setResult(null)

    const u = username.trim()
    const k = apiKey.trim()
    if (!u) { setError('Enter a GitHub username'); return }
    if (!k) { setError('Enter your Gemini API key'); return }

    setLoading(true)
    try {
      const commits = await fetchCommits(u)
      setCommitsCount(commits.length)
      const personality = await analyzePersonality(k, commits)
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
      backgroundColor: '#0a0a0f',
      scale: 2,
      useCORS: true,
    })
    const link = document.createElement('a')
    link.download = `${username}-commitconfessions.png`
    link.href = canvas.toDataURL()
    link.click()
  }

  return (
    <div className="min-h-screen flex flex-col items-center px-4 py-12">
      {/* Header */}
      <div className="text-center mb-12 animate-float">
        <div className="text-5xl mb-4">💾</div>
        <h1 className="font-retro text-lg sm:text-xl text-fuchsia-400 mb-3 glitch">
          COMMITCONFESSIONS
        </h1>
        <p className="text-cyan-300 font-pixel text-lg max-w-md">
          your git therapy session. paste your username. confess your code sins.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-4 mb-8">
        <div>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="GitHub username"
            className="w-full px-4 py-3 bg-black/50 border border-fuchsia-500/30 rounded-lg text-white font-pixel text-lg placeholder:text-gray-600 focus:outline-none focus:border-fuchsia-400 focus:shadow-[0_0_15px_rgba(255,0,255,0.2)] transition-all"
          />
        </div>
        <div>
          <input
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            type="password"
            placeholder="Gemini API key (get one free at aistudio.google.com)"
            className="w-full px-4 py-3 bg-black/50 border border-cyan-500/30 rounded-lg text-white font-pixel text-sm placeholder:text-gray-600 focus:outline-none focus:border-cyan-400 focus:shadow-[0_0_15px_rgba(0,255,255,0.2)] transition-all"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full py-4 bg-gradient-to-r from-fuchsia-600 to-cyan-600 rounded-lg font-retro text-sm text-white hover:from-fuchsia-500 hover:to-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all card-glow"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin">◌</span>
              ANALYZING YOUR SINS...
            </span>
          ) : (
            'GENERATE MY CARD'
          )}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="text-red-400 font-pixel text-lg mb-8 text-center max-w-md">
          ⚡ {error} ⚡
        </div>
      )}

      {/* Loading spinner */}
      {loading && (
        <div className="text-cyan-300 font-pixel text-xl animate-flicker mb-8">
          reading commit history...
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="flex flex-col items-center gap-6 w-full max-w-2xl">
          <div ref={cardRef} className="w-full">
            <Card username={username} result={result} />
          </div>
          <div className="flex gap-4">
            <button
              onClick={downloadCard}
              className="px-6 py-3 bg-white/5 border border-cyan-500/30 rounded-lg font-pixel text-cyan-300 hover:bg-white/10 transition-all text-lg"
            >
              💾 SAVE IMAGE
            </button>
            <button
              onClick={() => { setResult(null); setUsername(''); setApiKey('') }}
              className="px-6 py-3 bg-white/5 border border-fuchsia-500/30 rounded-lg font-pixel text-fuchsia-300 hover:bg-white/10 transition-all text-lg"
            >
              ↺ TRY AGAIN
            </button>
          </div>
          <p className="text-gray-500 font-pixel text-sm mt-4 text-center">
            analyzed {commitsCount} commits from @{username}
          </p>
        </div>
      )}

      {/* Footer */}
      <footer className="mt-auto pt-16 pb-6 text-gray-600 font-pixel text-sm text-center">
        <p>no data is stored. your API key stays on your device.</p>
        <p className="mt-1">built with Gemini + GitHub API</p>
      </footer>
    </div>
  )
}
