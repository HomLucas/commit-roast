export interface CommitData {
  message: string
  date: string
  repo: string
  url: string
}

export async function fetchCommits(username: string): Promise<CommitData[]> {
  const reposRes = await fetch(
    `https://api.github.com/users/${username}/repos?per_page=50&sort=pushed&type=all`
  )
  if (!reposRes.ok) {
    if (reposRes.status === 404) throw new Error('User not found')
    if (reposRes.status === 403) throw new Error('GitHub API rate limit. Try again later.')
    throw new Error(`GitHub API error (${reposRes.status})`)
  }

  const repos: { name: string; full_name: string; fork: boolean }[] = await reposRes.json()
  if (repos.length === 0) throw new Error('No repos found for this user')

  const allCommits: CommitData[] = []
  const seen = new Set<string>()

  // Try with author filter first
  for (const repo of repos.slice(0, 10)) {
    try {
      const res = await fetch(
        `https://api.github.com/repos/${repo.full_name}/commits?per_page=5&author=${username}`
      )
      if (!res.ok) continue
      const data: any[] = await res.json()
      if (!Array.isArray(data)) continue
      for (const c of data) {
        const msg = c?.commit?.message?.split('\n')[0]
        if (!msg || seen.has(msg)) continue
        seen.add(msg)
        allCommits.push({
          message: msg,
          date: c.commit.author?.date || c.commit.committer?.date || '',
          repo: repo.name,
          url: c.html_url || '',
        })
      }
    } catch { /* skip */ }
  }

  // Fallback: if no commits found, try without author filter
  if (allCommits.length === 0) {
    for (const repo of repos.slice(0, 10)) {
      try {
        const res = await fetch(
          `https://api.github.com/repos/${repo.full_name}/commits?per_page=5`
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
        }
      } catch { /* skip */ }
    }
  }

  if (allCommits.length === 0) throw new Error('No commits found for this user')
  return allCommits
}
