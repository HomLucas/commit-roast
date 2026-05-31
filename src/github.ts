export interface CommitData {
  message: string
  date: string
  repo: string
  url: string
}

function getCache(username: string): CommitData[] | null {
  try {
    const raw = localStorage.getItem(`cc_cache_${username}`)
    if (!raw) return null
    const { data, time } = JSON.parse(raw)
    if (Date.now() - time > 3600000) { // 1 hour expiry
      localStorage.removeItem(`cc_cache_${username}`)
      return null
    }
    return data
  } catch { return null }
}

function setCache(username: string, data: CommitData[]) {
  try {
    localStorage.setItem(`cc_cache_${username}`, JSON.stringify({ data, time: Date.now() }))
  } catch { /* storage full, skip */ }
}

export async function fetchCommits(username: string): Promise<CommitData[]> {
  const cached = getCache(username)
  if (cached) return cached

  const reposRes = await fetch(
    `https://api.github.com/users/${username}/repos?per_page=5&sort=pushed&type=all`
  )
  if (reposRes.status === 403) throw new Error('GitHub API rate limit. Try again later.')
  if (reposRes.status === 404) throw new Error('User not found')
  if (!reposRes.ok) throw new Error(`GitHub error (${reposRes.status})`)

  const repos: { name: string; full_name: string }[] = await reposRes.json()
  if (repos.length === 0) throw new Error('No repos found')

  const allCommits: CommitData[] = []
  const seen = new Set<string>()

  for (const repo of repos) {
    if (allCommits.length >= 30) break
    try {
      const res = await fetch(
        `https://api.github.com/repos/${repo.full_name}/commits?per_page=15`
      )
      if (!res.ok) continue
      const data: any[] = await res.json()
      if (!Array.isArray(data)) continue
      for (const c of data) {
        const msg = c?.commit?.message?.split('\n')[0]
        if (!msg || seen.has(msg) || msg.length < 3) continue
        seen.add(msg)
        allCommits.push({
          message: msg,
          date: c.commit.author?.date || c.commit.committer?.date || '',
          repo: repo.name,
          url: c.html_url || '',
        })
        if (allCommits.length >= 30) break
      }
    } catch { /* skip */ }
  }

  if (allCommits.length < 3) throw new Error('Not enough commits found (need at least 3)')

  setCache(username, allCommits)
  return allCommits
}
