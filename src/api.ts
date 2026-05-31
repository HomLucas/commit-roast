export interface PersonalityResult {
  type: string
  subtitle: string
  moodScore: number
  moodLabel: string
  topCommits: string[]
  diagnosis: string
  prescription: string
  stats: {
    totalCommits: number
    peakHour: string
    favoriteDay: string
  }
}

export type Provider = 'openai' | 'groq' | 'anthropic'

function buildPrompt(commits: { message: string; date: string; repo: string }[]): string {
  const text = commits.slice(0, 50).map((c) =>
    `- "${c.message}" (${c.date.slice(0, 10)}, repo: ${c.repo})`
  ).join('\n')

  return `You are a quirky AI therapist analyzing a developer's git history. Given these commit messages, generate a fun personality profile.

Commits:
${text}

Return ONLY valid JSON (no markdown, no backticks) with this exact structure:
{
  "type": "A creative personality title like 'The Night Owl Architect' or 'The Ship-It Enthusiast' or 'The Refactor Monk'",
  "subtitle": "A one-line witty description of their coding style",
  "moodScore": "A number 0-100 representing the overall mood/tone of their commits",
  "moodLabel": "A label for that score like 'Chaotic Neutral', 'Determined', 'Exhausted Genius'",
  "topCommits": ["the 3 funniest or most revealing commit messages, just the message text"],
  "diagnosis": "A 1-2 sentence mock clinical diagnosis of their coding habits",
  "prescription": "A funny but wise piece of advice for them as a developer",
  "stats": {
    "totalCommits": ${commits.length},
    "peakHour": "the most common hour they commit based on commit times",
    "favoriteDay": "the most common day of the week"
  }
}`;
}

async function parseJsonResponse(text: string): Promise<PersonalityResult> {
  const cleaned = text.replace(/```(json)?/g, '').trim()
  const result = JSON.parse(cleaned)
  result.topCommits = result.topCommits?.slice(0, 3) || []
  return result
}

async function callOpenAI(key: string, prompt: string): Promise<PersonalityResult> {
  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
    body: JSON.stringify({ model: 'gpt-4o', messages: [{ role: 'user', content: prompt }], temperature: 1.0, max_tokens: 1024 }),
  })
  if (!res.ok) {
    const body = await res.text()
    if (res.status === 401) throw new Error('Invalid OpenAI key. Get one at platform.openai.com.')
    if (res.status === 429) throw new Error('OpenAI quota exceeded. Check billing at platform.openai.com.')
    throw new Error(`OpenAI error: ${body.slice(0, 200)}`)
  }
  const data = await res.json()
  const text = data?.choices?.[0]?.message?.content
  if (!text) throw new Error('OpenAI returned no response')
  return parseJsonResponse(text)
}

async function callGroq(key: string, prompt: string): Promise<PersonalityResult> {
  const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
    body: JSON.stringify({ model: 'llama-3.3-70b-versatile', messages: [{ role: 'user', content: prompt }], temperature: 1.0, max_tokens: 1024 }),
  })
  if (!res.ok) {
    const body = await res.text()
    if (res.status === 401) throw new Error('Invalid Groq key. Get one free at console.groq.com.')
    if (res.status === 429) throw new Error('Groq rate limit. Wait a moment or upgrade at console.groq.com.')
    throw new Error(`Groq error: ${body.slice(0, 200)}`)
  }
  const data = await res.json()
  const text = data?.choices?.[0]?.message?.content
  if (!text) throw new Error('Groq returned no response')
  return parseJsonResponse(text)
}

async function callAnthropic(key: string, prompt: string): Promise<PersonalityResult> {
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-api-key': key, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 1024, messages: [{ role: 'user', content: prompt }] }),
  })
  if (!res.ok) {
    const body = await res.text()
    if (res.status === 401) throw new Error('Invalid Anthropic key. Get one at console.anthropic.com.')
    if (res.status === 429) throw new Error('Anthropic quota exceeded. Check billing at console.anthropic.com.')
    throw new Error(`Anthropic error: ${body.slice(0, 200)}`)
  }
  const data = await res.json()
  const text = data?.content?.[0]?.text
  if (!text) throw new Error('Anthropic returned no response')
  return parseJsonResponse(text)
}

export async function analyzePersonality(
  provider: Provider,
  apiKey: string,
  commits: { message: string; date: string; repo: string }[]
): Promise<PersonalityResult> {
  const prompt = buildPrompt(commits)
  switch (provider) {
    case 'openai': return callOpenAI(apiKey, prompt)
    case 'groq': return callGroq(apiKey, prompt)
    case 'anthropic': return callAnthropic(apiKey, prompt)
  }
}
