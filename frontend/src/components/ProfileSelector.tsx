import { useEffect, useState } from 'react'
import type { Profile } from '../api'
import { createProfile, deleteProfile, fetchProfiles, getProfile } from '../api'

interface ProfileSelectorProps {
  selectedId: string | null
  onSelect: (profile: Profile | null) => void
}

export default function ProfileSelector({ selectedId, onSelect }: ProfileSelectorProps) {
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [loading, setLoading] = useState(true)
  const [newName, setNewName] = useState('')
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)

  const load = async () => {
    setError(null)
    try {
      const list = await fetchProfiles()
      setProfiles(list)
      if (list.length && !selectedId) onSelect(list[0])
      if (selectedId && !list.find((p) => p.id === selectedId)) onSelect(list[0] ?? null)
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Could not load profiles.'
      setError(`Backend not reachable. Start the server first (see README). ${msg}`)
      setProfiles([])
      onSelect(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    const name = newName.trim() || 'My profile'
    setCreating(true)
    setError(null)
    setSuccess(null)
    try {
      const p = await createProfile(name)
      setProfiles((prev) => [...prev, p])
      setNewName('')
      onSelect(p)
      setSuccess(`Profile "${p.name}" created.`)
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create profile. Is the backend running on port 8000?')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async () => {
    if (!selectedId || !selected) return
    if (!window.confirm(`Delete profile "${selected.name}"? This cannot be undone.`)) return
    setDeleting(true)
    setError(null)
    setSuccess(null)
    try {
      await deleteProfile(selectedId)
      const remaining = profiles.filter((p) => p.id !== selectedId)
      setProfiles(remaining)
      onSelect(remaining[0] ?? null)
      setSuccess('Profile deleted.')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete profile.')
    } finally {
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <div className="rounded-lg border border-navy-600 bg-navy-800/50 px-4 py-3 text-sm text-navy-400">
        Loading profiles…
      </div>
    )
  }

  const selected = profiles.find((p) => p.id === selectedId)

  return (
    <div className="rounded-lg border border-navy-600 bg-navy-800/50 p-4">
      <h2 className="mb-3 text-lg font-semibold text-slate-200">Profile & watchlist</h2>
      {error && (
        <div className="mb-3 rounded border border-accent-500/80 bg-accent-900/40 px-3 py-2 text-sm text-accent-300">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-3 rounded border border-accent-500/80 bg-accent-900/30 px-3 py-2 text-sm text-accent-300">
          {success}
        </div>
      )}
      <div className="flex flex-wrap items-end gap-3">
        <div className="min-w-[160px]">
          <label className="mb-1 block text-xs text-navy-400">Profile</label>
          <select
            value={selectedId ?? ''}
            onChange={async (e) => {
              const id = e.target.value
              if (!id) {
                onSelect(null)
                return
              }
              try {
                const p = await getProfile(id)
                onSelect(p)
              } catch {
                const p = profiles.find((x) => x.id === id)
                onSelect(p ?? null)
              }
            }}
            className="w-full rounded border border-navy-600 bg-navy-800 px-3 py-2 text-sm text-white focus:border-accent-500 focus:outline-none focus:ring-1 focus:ring-accent-500"
          >
            <option value="">— Select —</option>
            {profiles.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        {selected && (
          <button
            type="button"
            onClick={handleDelete}
            disabled={deleting}
            className="rounded border border-accent-600 bg-accent-900/50 px-3 py-2 text-sm font-medium text-accent-300 hover:bg-accent-800/50 disabled:opacity-50"
            title="Delete this profile"
          >
            {deleting ? 'Deleting…' : 'Delete profile'}
          </button>
        )}
        <form onSubmit={handleCreate} className="flex flex-wrap items-end gap-2">
          <div className="min-w-[140px]">
            <label className="mb-1 block text-xs text-navy-400">New profile</label>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Profile name"
              className="w-full rounded border border-navy-600 bg-navy-800 px-3 py-2 text-sm text-white placeholder-navy-400 focus:border-accent-500 focus:outline-none focus:ring-1 focus:ring-accent-500"
              disabled={creating}
            />
          </div>
          <button
            type="submit"
            disabled={creating}
            className="rounded bg-navy-600 px-3 py-2 text-sm font-medium text-white hover:bg-navy-500 disabled:opacity-50"
          >
            {creating ? 'Creating…' : 'Create'}
          </button>
        </form>
      </div>
      {selected && (
        <p className="mt-2 text-xs text-navy-400">
          Watchlist: {selected.tickers.length ? selected.tickers.join(', ') : '(empty — add tickers below)'}
        </p>
      )}
    </div>
  )
}
