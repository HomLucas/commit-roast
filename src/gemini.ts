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

export async function analyzePersonality(
  apiKey: string,
  commits: { message: string; date: string; repo: string }[]
): Promise<PersonalityResult> {
  const commitText = commits
    .slice(0, 50)
    .map((c) => `- "${c.message}" (${c.date.slice(0, 10)}, repo: ${c.repo})`)
    .join('\n')

  const prompt = `You are a quirky AI therapist analyzing a developer's git history. Given these commit messages, generate a fun personality profile.

Commits:
${commitText}

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
    "peakHour": "the most common hour they commit based on commit times, like '2 AM' or '3 PM'",
    "favoriteDay": "the most common day of the week"
  }
}`

  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: {
          temperature: 1.0,
          maxOutputTokens: 1024,
        },
      }),
    }
  )

  if (!res.ok) {
    const body = await res.text()
    if (res.status === 403 || res.status === 400) {
      throw new Error('Invalid API key. Get one free at aistudio.google.com.')
    }
    if (res.status === 429) {
      throw new Error('Gemini API quota exceeded. Add a billing account at console.cloud.google.com/billing (free tier, won\'t charge you) or try again later.')
    }
    throw new Error(`AI error: ${body.slice(0, 200)}`)
  }

  const data = await res.json()
  const text = data?.candidates?.[0]?.content?.parts?.[0]?.text
  if (!text) throw new Error('AI returned no response')

  const cleaned = text.replace(/```(json)?/g, '').trim()
  const result: PersonalityResult = JSON.parse(cleaned)
  result.topCommits = result.topCommits?.slice(0, 3) || []
  return result
}
