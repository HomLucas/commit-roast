export interface CommitData {
  message: string
  date: string
  repo: string
  url: string
}

export async function fetchCommits(username: string): Promise<CommitData[]> {
  // Fetch top repos
  const reposRes = await fetch(
    `https://api.github.com/users/${username}/repos?per_page=10&sort=pushed&type=all`
  )
  if (reposRes.status === 403) throw new Error('GitHub API rate limit. Try again later.')
  if (reposRes.status === 404) throw new Error('User not found')
  if (!reposRes.ok) throw new Error(`GitHub error (${reposRes.status})`)

  const repos: { name: string; full_name: string }[] = await reposRes.json()
  if (repos.length === 0) throw new Error('No repos found')

  const allCommits: CommitData[] = []
  const seen = new Set<string>()

  // Check top 3 repos, 3 commits each = 4 total API calls
  for (const repo of repos.slice(0, 3)) {
    try {
      const res = await fetch(
        `https://api.github.com/repos/${repo.full_name}/commits?per_page=3`
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

  if (allCommits.length === 0) throw new Error('No commits found')
  return allCommits
}
