export interface CommitData {
  message: string
  date: string
  repo: string
  url: string
}

export async function fetchCommits(username: string): Promise<CommitData[]> {
  const reposRes = await fetch(
    `https://api.github.com/users/${username}/repos?per_page=30&sort=pushed&type=owner`
  )
  if (!reposRes.ok) {
    if (reposRes.status === 404) throw new Error('User not found')
    if (reposRes.status === 403) throw new Error('GitHub API rate limit. Try again later.')
    throw new Error(`GitHub API error (${reposRes.status})`)
  }

  const repos: { name: string; full_name: string }[] = await reposRes.json()
  if (repos.length === 0) throw new Error('No repos found for this user')

  const allCommits: CommitData[] = []

  for (const repo of repos.slice(0, 10)) {
    try {
      const res = await fetch(
        `https://api.github.com/repos/${repo.full_name}/commits?per_page=10&author=${username}`
      )
      if (!res.ok) continue
      const data: { commit: { message: string; author: { date: string } }; html_url: string }[] = await res.json()
      for (const c of data) {
        allCommits.push({
          message: c.commit.message.split('\n')[0],
          date: c.commit.author.date,
          repo: repo.name,
          url: c.html_url,
        })
      }
    } catch {
      // skip repos that fail
    }
  }

  if (allCommits.length === 0) throw new Error('No commits found for this user')

  return allCommits
}
