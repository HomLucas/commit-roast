export interface CommitData {
  message: string
  date: string
  repo: string
  url: string
}

export async function fetchCommits(username: string, token?: string): Promise<CommitData[]> {
  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`

  const reposRes = await fetch(
    `https://api.github.com/users/${username}/repos?per_page=10&sort=pushed&type=all`,
    { headers }
  )
  if (reposRes.status === 403) throw new Error('GitHub API rate limit. Try again later or add a GitHub token.')
  if (reposRes.status === 404) throw new Error('User not found')
  if (!reposRes.ok) throw new Error(`GitHub error (${reposRes.status})`)

  const repos: { name: string; full_name: string }[] = await reposRes.json()
  if (repos.length === 0) throw new Error('No repos found')

  const allCommits: CommitData[] = []
  const seen = new Set<string>()
  const MAX_COMMITS = 30

  for (const repo of repos) {
    if (allCommits.length >= MAX_COMMITS) break
    try {
      const needed = MAX_COMMITS - allCommits.length
      const res = await fetch(
        `https://api.github.com/repos/${repo.full_name}/commits?per_page=${Math.min(needed, 15)}`,
        { headers }
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
        if (allCommits.length >= MAX_COMMITS) break
      }
    } catch { /* skip */ }
  }

  if (allCommits.length < 3) throw new Error('Not enough commits found (need at least 3)')
  return allCommits
}
